import json, os
import secrets
import requests
from multiprocessing import RLock

import logging
log = logging.getLogger("ocpi")
import ocpi.models.credentials as mc



class CredentialsManager:
    def __init__(self, credentials_roles: mc.CredentialsRoleValidator, url, **kwds):
        self.credentials_roles = credentials_roles
        self.url = url
        super().__init__(**kwds)
    
        
    def createOcpiHeader(self, token):
        return {
            "Authorization": "Token " + token,
            "X-Request-ID": secrets.token_urlsafe(8),
        }

    def _getEndpoints(self, client_url, client_version="2.1.1",access_client=None):
        endpoints = []
        header = self.createOcpiHeader(access_client)
        try:
            response = requests.get(f"{client_url}/{client_version}",headers=header)
            endpoints = response.json()["data"]["endpoints"]
        except requests.exceptions.ConnectionError:
            log.error(f"no version details, connection to {client_url} failed")
        except Exception:
            log.exception(
                f"could not get version details from {client_url}, {client_version}"
            )
        return endpoints

    def _sendRegisterResponse(self, url, version, token, access_client):
        data = {
            "token": token, 
            "url": self.url, 
            "business_details": self.credentials_roles[0]["business_details"],
            "party_id": self.credentials_roles[0]["party_id"],
            "country_code": self.credentials_roles[0]["country_code"],
            }
        header = self.createOcpiHeader(access_client)
        log.info(f"sending post request {data}")
        resp = requests.post(f"{url}/{version}/credentials", json=data, headers=header)
        if resp.status_code == 405:
            resp = requests.put(
                f"{url}/{version}/credentials", json=data, headers=header
            )
        resp.raise_for_status()
        # catch as requests.exceptions.HTTPError
        # get e.response.status_code

        data = resp.json()
        log.info(f"registration successful: {data}")
        return data["data"]["token"]
        # TODO check roles and business details
        # data['data']['roles']

    def _pushObjects(self, objects, method, token, endpoint_url, with_path=True):
        headers = self.createOcpiHeader(token)
        for r in objects:
            try:
                if with_path:
                    url = (
                        f"{endpoint_url}/{r['country_code']}/{r['party_id']}/{r['id']}"
                    )
                else:
                    url = endpoint_url

                if method == "PUT":
                    res = requests.put(url, headers=headers, json=r)
                elif method == "PATCH":
                    res = requests.patch(url, headers=headers, json=r)
                elif method == "POST":
                    res = requests.post(url, headers=headers, json=r)
                else:
                    raise Exception("invalid method provided: {method}")

                res.raise_for_status()
            except requests.exceptions.HTTPError as e:
                log.warning(
                    f"ocpi {method} object {e.response.status_code} - {e.response.text} - {url}"
                )
            except requests.exceptions.ConnectionError:
                log.warning(f"could not connect to {url}")
            except Exception:
                log.exception(f"error sending to {url}")

    def makeRegistration(self, payload: mc.CredentialsValidator, tokenA: str):
        # tokenA used to get here for initial handshake
        log.debug(f"making registration")
        self._deleteToken(tokenA)
        tokenB = payload["token"]
        client_url = payload["url"]

        tokenC = secrets.token_urlsafe(32)  # plain
        newCredentials = {
            "token": tokenC,  # this is plain text and not base64
            "url": self.url,
            "roles": self.credentials_roles,
        }
        endpoints = self._getEndpoints(client_url)
        self._updateToken(tokenC, client_url, tokenB, endpoints)
        return newCredentials

    def versionUpdate(self, payload: mc.CredentialsValidator, token: str):
        return self.makeRegistration(payload, token)

    def unregister(self, token):
        res = self._deleteToken(token)
        if res is None:
            return "method not allowed", 405
        return "", 200

    def isAuthenticated(self, token):
        raise NotImplementedError()

    def sendToModule(self, objects, module, method="PUT", with_path=True):
        raise NotImplementedError()

    def _updateToken(self, token, client_url, client_token, endpoint_list=None):
        raise NotImplementedError()

    def _deleteToken(self, token):
        raise NotImplementedError()

    def getCredentials(self, token: str) -> mc.CredentialsValidator:
        return {
            "token": token,
            "url": self.url,
            "roles": [self.credentials_roles],
        }

class CredentialsDictMan(CredentialsManager):
    
    lock = RLock()

    def __init__(
        self, credentials_roles: mc.CredentialsRoleValidator, url, filename="ocpi_creds.json"
    ):
        self.filename = filename
        with CredentialsDictMan.lock:
            if not os.path.isfile(filename):
                self.writeJson({})
        super().__init__(credentials_roles, url)

    def getUrl(self):
        return self.url
    
    def readJson(self):
        with CredentialsDictMan.lock:
            with open(self.filename, "r") as f:
                return json.load(f)

    def writeJson(self, endpoints):
        with CredentialsDictMan.lock:
            with open(self.filename, "w") as f:
                json.dump(endpoints, f, indent=4, sort_keys=False)

    def isAuthenticated(self, token):
        return token in self.readJson()
    
    def getRole(self, token):
        return self.getToken(token)["role"].get("type")
    
    def isLocationAllowed(self, token, location_id):
        return location_id in self.getToken(token)["role"].get("allowed_locations")
    
    def getAllowedLocations(self, token):
        return self.getToken(token)["role"].get("allowed_locations")

    def sendToModule(self, objects, module, method="PUT", with_path=True):
        for token in self.readJson().values():
            actual_module = list(
                filter(lambda t: t["identifier"] == module, token["endpoints"])
            )
            if actual_module:
                self._pushObjects(
                    objects, method, token["client_token"], actual_module[0]["url"]
                )

    def _updateToken(self, token, client_url, client_token, endpoint_list=None):
        data = {
            "client_url": client_url,
            "client_token": client_token,
            "endpoints": endpoint_list or [],
        }
        with CredentialsDictMan.lock:
            tokens = self.readJson()
            tokens[token] = data
            self.writeJson(tokens)
        log.debug(f"current tokens: {tokens}")

    def _deleteToken(self, token):
        with CredentialsDictMan.lock:
            tokens = self.readJson()
            tokens.pop(token, None)
            self.writeJson(tokens)
   
    def getToken(self, token:str):
        return self.readJson().get(token)

    def getModuleEndpoint(self, token:str, ocpiModule:str):
        token_object = self.readJson().get(token)
        endpoint=next(endpoint for endpoint in token_object["endpoints"] if endpoint['identifier']==ocpiModule)
        return endpoint.get("url")
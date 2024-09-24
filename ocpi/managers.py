from __future__ import annotations

import base64
import json
import logging
import os
import secrets
from multiprocessing import RLock
from copy import deepcopy

import requests
from werkzeug.exceptions import NotFound, BadRequest

import ocpi.models.credentials as mc
import ocpi.exceptions as oe


from pymongo import MongoClient
log = logging.getLogger("ocpi")
logging.getLogger('pymongo').setLevel(logging.WARNING)
CONNECTION_STRING = f'mongodb://{os.environ["MONGO_USER"]}:{os.environ["MONGO_PWD"]}@{os.environ["MONGO_HOST"]}:{os.environ["MONGO_PORT"]}'
mongo = MongoClient(CONNECTION_STRING)
ocpi_db=mongo["ocpi"]
# sender interface


class CredentialsManager:
    def __init__(self, credentials_roles: mc.CredentialsRole, url, **kwds):
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

    def makeRegistration(self, payload: mc.Credentials, tokenA: str):
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

    def versionUpdate(self, payload: mc.Credentials, token: str):
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

    def getCredentials(self, token: str) -> mc.Credentials:
        return {
            "token": token,  # this is plain text and not base64
            "url": self.url,
            "roles": [self.credentials_roles],
        }

class CredentialsDictMan(CredentialsManager):

    lock = RLock()

    def __init__(
        self, credentials_roles: mc.CredentialsRole, url, filename="ocpi_creds.json"
    ):
        self.filename = filename
        with CredentialsDictMan.lock:
            if not os.path.isfile(filename):
                self.writeJson({})
        super().__init__(credentials_roles, url)

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



class LocationManager():
    def __init__(self):
        self.locations = ocpi_db["locations"]
        self.evses = ocpi_db["evses"]
        self.connectors = ocpi_db["connectors"]

    def getLocation(self, country_id, party_id, location_id):
        location=self.locations.find_one({"_id":f"{location_id}"})
        if location==None: raise oe.InvalidLocationError
        location.pop("_id")
        evses=self.evses.find({"location_id":location_id})
        location["evses"]=[self.getEVSE(country_id, party_id, location_id, evse["evse_uid"]) for evse in evses]
        return location
        
    def putLocation(self, country_id, party_id, location_id, location):
        if location_id!=location["id"]: raise BadRequest("id in the location object does not match the id in the URL")
        evses=deepcopy(location["evses"])
        location["evses"]=[f'{location_id}-{evse["uid"]}' for evse in evses]
        for evse in evses:
            self.putEVSE(country_id, party_id, location_id, evse["uid"], evse)
        try:
            location["_id"]=location["id"]
            self.locations.insert_one(location)
        except:
            print(f"already exists, patching location_id:{location_id}, with:{location}")
            self.patchLocation(country_id, party_id, location_id, location)
            
    def patchLocation(self, country_id, party_id, location_id, location):
        r=self.locations.update_one({"_id":f"{location_id}"},{"$set":location})
        if r.matched_count<1: 
            raise oe.InvalidLocationError
    
    def getEVSE(self, country_id, party_id, location_id, evse_uid):
        evse=self.evses.find_one({"_id":f"{location_id}-{evse_uid}"})
        if evse==None: raise oe.InvalidLocationError
        evse["evse"]["connectors"]=[connector["connector"] for connector in self.connectors.find({"location_id":location_id,"evse_uid":evse_uid})]
        return evse["evse"]

        
    def putEVSE(self, country_id, party_id, location_id, evse_uid, evse):
        if evse_uid!=evse["uid"]: raise BadRequest("uid in the evse object does not match the uid in the URL")
        connectors=deepcopy(evse["connectors"])
        evse["connectors"]=[f'{location_id}-{evse_uid}-{connector["id"]}' for connector in connectors]
        for connector in connectors:
            self.putConnector(country_id, party_id, location_id, evse_uid, connector["id"], connector)
        try:
            self.evses.insert_one({
                "_id":f"{location_id}-{evse_uid}",
                "location_id":location_id,"evse_uid":evse_uid,"evse":evse})
        except:
            print(f"already exists, patching location_id:{location_id}, evse_uid:{evse_uid} with:{evse}")
            self.patchEVSE(country_id, party_id, location_id, evse_uid, evse)
            
    def patchEVSE(self, country_id, party_id, location_id, evse_uid, evse):
        update_dict={"location_id":location_id,"evse_uid":evse_uid}|{f"evse.{key}": value for key, value in evse.items()}
        r=self.evses.update_one({"_id":f"{location_id}-{evse_uid}"},{"$set":update_dict})
        if r.matched_count<1: 
            raise oe.InvalidLocationError
    
    
    def getConnector(self, country_id, party_id, location_id, evse_uid, connector_id):
        connector = self.connectors.find_one({"_id":f"{location_id}-{evse_uid}-{connector_id}"})
        print(connector)
        if connector==None: raise oe.InvalidLocationError
        return connector["connector"]
        
    def putConnector(self, country_id, party_id, location_id, evse_uid, connector_id, connector):
        if connector_id!=connector["id"]: raise BadRequest("id in the connector object does not match the id in the URL")
        try:
            self.connectors.insert_one({
                "_id":f"{location_id}-{evse_uid}-{connector_id}",
                "location_id":location_id,"evse_uid":evse_uid,"connector_id":connector_id,"connector":connector})
        except:
            print(f"already exists, patching location_id:{location_id}, evse_uid:{evse_uid}, connector_id:{connector_id}, with:{connector}")
            self.patchConnector(country_id, party_id, location_id, evse_uid, connector_id, connector)
            
    def patchConnector(self, country_id, party_id, location_id, evse_uid, connector_id, connector):
        r=self.connectors.update_one({
                    "_id":f"{location_id}-{evse_uid}-{connector_id}"},{"$set":{
                    "location_id":location_id,"evse_uid":evse_uid,"connector_id":connector_id}|{f"connector.{key}": value for key, value in connector.items()}})
        if r.matched_count<1: 
            raise oe.InvalidLocationError


class VersionManager:
    def __init__(self, base_url, endpoints: dict, ocpi_version="2.2"):
        self._base_url = base_url
        self._ocpi_version = ocpi_version
        self._details = self._makeDetails(endpoints)

        # TODO support multiple Versions

    def _makeDetails(self, endpoints):
        res = []
        for ep_name, role in endpoints.items():
            if ep_name!="internal":
                e = {}
                e["identifier"] = ep_name
                e["role"] = role
                e["url"] = f"{self._base_url}/{self._ocpi_version}/{ep_name}"
                res.append(e)
        return res

    def versions(self):
        return [
                {
                    "version": self._ocpi_version,
                    "url": self._base_url + "/" + self._ocpi_version,
                }
            ]

    def details(self):
        return {"version": self._ocpi_version, "endpoints": self._details}
    
    
class SessionManager:
    def __init__(self):
        self.sessions = {}

    def getSessions(self, begin, end, offset, limit):
        log.info("get sessions")
        return list(self.sessions.values())[offset : offset + limit], {}

    def getSession(self, country_id, party_id, session_id):
        log.info(f"getting session {session_id}")
        return self.sessions[session_id]

    def createSession(self, country_id, party_id, session):
        log.info(f"create session {session}")
        self.sessions[session["id"]]=session

    def patchSession(self, country_id, party_id, session_id, sessionPart):
        log.info(f"patching session {session_id} with {sessionPart}")
        self.sessions[session_id].update(sessionPart)



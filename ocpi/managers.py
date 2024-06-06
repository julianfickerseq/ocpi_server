#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  1 12:47:48 2021

@author: maurer
"""
from __future__ import annotations

import base64
import json
import logging
import os
import secrets
from multiprocessing import RLock
import copy

import requests

import ocpi.models.credentials as mc


def createOcpiHeader(token,encode:bool=False):
    encToken = base64.b64encode(token.encode("utf-8")).decode("utf-8") if encode else token
    return {
        "Authorization": "Token " + encToken,
        "X-Request-ID": secrets.token_urlsafe(8),
    }


log = logging.getLogger("ocpi")
# sender interface


class CredentialsManager:
    def __init__(self, credentials_roles: mc.CredentialsRole, url, **kwds):
        self.credentials_roles = credentials_roles
        self.url = url
        super().__init__(**kwds)

    def _getEndpoints(self, client_url, client_version="2.1.1",access_client=None):
        endpoints = []
        header = createOcpiHeader(access_client)
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
        header = createOcpiHeader(access_client)
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
        headers = createOcpiHeader(token)
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


class LocationManager(object):
    def __init__(self):
        self.locations = {}
    
    def populateEvses(self, location_id, evses):
        self.locations[location_id]["evses"]={}
        for evse in evses:
            self.locations[location_id]["evses"][evse["uid"]]=evse
            self.populateConnectors(location_id, evse["uid"],evse["connectors"].copy())

    def translateEvses(self, location):
        for evse_id,evse in location["evses"].items():
            location["evses"][evse_id]=self.translateConnectors(evse)
        location["evses"]=list(location["evses"].values())
        return location

    def populateConnectors(self, location_id, evse_id, connectors):
        self.locations[location_id]["evses"][evse_id]["connectors"]={}
        for connector in connectors:
            self.locations[location_id]["evses"][evse_id]["connectors"][connector["id"]]=connector
    
    def translateConnectors(self, evse):
        evse["connectors"]=list(evse["connectors"].values())
        return evse

    def getLocations(self, begin, end, offset, limit):
        log.info(f"getting locations")
        return list(self.locations.values())[offset : offset + limit], {}

    def getLocation(self, country_id, party_id, location_id):
        log.info(f"getting location {location_id}")
        return self.translateEvses(self.locations[location_id].copy())

    def putLocation(self, country_id, party_id, location_id, location):
        log.info(f"putting location: {location}")
        self.locations[location_id] = location
        self.populateEvses(location_id, location["evses"].copy())
        
    def patchLocation(self, country_id, party_id, location_id, location):
        log.info(f"patching location: {location}")
        self.locations[location_id].update(location)

    def getEVSE(self, country_id, party_id, location_id, evse_id):
        log.info(f"getting evse {location_id}/{evse_id}")
        return self.translateConnectors(self.locations[location_id]["evses"][evse_id].copy())

    def putEVSE(self, country_id, party_id, location_id, evse_id, evse):
        log.info(f"putting evse {location_id}/{evse_id}: {evse}")
        self.locations[location_id]["evses"][evse_id] = evse
        self.populateConnectors(location_id, evse_id, evse["connectors"].copy())

    def patchEVSE(self, country_id, party_id, location_id, evse_id, evse):
        log.info(f"patching evse {location_id}/{evse_id}: {evse}")
        self.locations[location_id]["evses"][evse_id].update(evse)

    def getConnector(self, country_id, party_id, location_id, evse_id, connector_id):
        log.info(f"getting connector {location_id}/{evse_id}/{connector_id}")
        return self.locations[location_id]["evses"][evse_id]["connectors"][connector_id]

    def putConnector(self, country_id, party_id, location_id, evse_id, connector_id, connector):
        log.info(f"putting connector {location_id}/{evse_id}/{connector_id}: {connector}")
        self.locations[location_id]["evses"][evse_id]["connectors"][connector_id] = connector

    def patchConnector(self, country_id, party_id, location_id, evse_id, connector_id, connector):
        log.info(f"patching connector {location_id}/{evse_id}/{connector_id}: {connector}")
        self.locations[location_id]["evses"][evse_id]["connectors"][connector_id].update(connector)


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
        log.debug("get sessions")
        return list(self.sessions.values())[offset : offset + limit], {}

    def getSession(self, country_id, party_id, session_id):
        log.debug("get session")
        return 204

    def createSession(self, country_id, party_id, session):
        log.debug("create session")
        return 204

    def patchSession(self, country_id, party_id, session_id, sessionPart):
        log.debug("patch session")
        pass

    def updateChargingPrefs(self, session_id, prefs):
        pass


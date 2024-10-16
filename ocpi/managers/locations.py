from ocpi.managers import ocpi_db
import ocpi.exceptions as oe
from werkzeug.exceptions import BadRequest
from copy import deepcopy



import logging
log = logging.getLogger("ocpi")

class LocationManager():
    def __init__(self):
        self.locations = ocpi_db["locations"]
        self.evses = ocpi_db["evses"]
        self.connectors = ocpi_db["connectors"]

    def getLocations(self, begin, end, offset, limit):
        return

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
            log.info(f"already exists, patching location_id:{location_id}, with:{location}")
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
            log.info(f"already exists, patching location_id:{location_id}, evse_uid:{evse_uid} with:{evse}")
            self.patchEVSE(country_id, party_id, location_id, evse_uid, evse)
            
    def patchEVSE(self, country_id, party_id, location_id, evse_uid, evse):
        update_dict={"location_id":location_id,"evse_uid":evse_uid}|{f"evse.{key}": value for key, value in evse.items()}
        r=self.evses.update_one({"_id":f"{location_id}-{evse_uid}"},{"$set":update_dict})
        if r.matched_count<1: 
            raise oe.InvalidLocationError
    
    
    def getConnector(self, country_id, party_id, location_id, evse_uid, connector_id):
        connector = self.connectors.find_one({"_id":f"{location_id}-{evse_uid}-{connector_id}"})
        if connector==None: raise oe.InvalidLocationError
        return connector["connector"]
        
    def putConnector(self, country_id, party_id, location_id, evse_uid, connector_id, connector):
        if connector_id!=connector["id"]: raise BadRequest("id in the connector object does not match the id in the URL")
        try:
            self.connectors.insert_one({
                "_id":f"{location_id}-{evse_uid}-{connector_id}",
                "location_id":location_id,"evse_uid":evse_uid,"connector_id":connector_id,"connector":connector})
        except:
            log.info(f"already exists, patching location_id:{location_id}, evse_uid:{evse_uid}, connector_id:{connector_id}, with:{connector}")
            self.patchConnector(country_id, party_id, location_id, evse_uid, connector_id, connector)
            
    def patchConnector(self, country_id, party_id, location_id, evse_uid, connector_id, connector):
        r=self.connectors.update_one({
                    "_id":f"{location_id}-{evse_uid}-{connector_id}"},{"$set":{
                    "location_id":location_id,"evse_uid":evse_uid,"connector_id":connector_id}|{f"connector.{key}": value for key, value in connector.items()}})
        if r.matched_count<1: 
            raise oe.InvalidLocationError


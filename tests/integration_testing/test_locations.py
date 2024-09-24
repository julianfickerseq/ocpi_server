import json
import sys, os, pathlib
import logging
import requests
from copy import deepcopy

logging.getLogger('ocpi')

with open(f'{sys.path[0]}/tests/integration_testing/location.json', 'r') as file:
    data = json.load(file)

##LOCATIONS
def test_put_location(client,headers):
    r_put=client.put("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877",json=data["89900877"],headers=headers)
    assert r_put.status_code==200

def test_get_location(client,headers):
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877",headers=headers)
    assert r_get.status_code==200
    assert data["89900877"]==r_get.json["data"]
    
def test_get_wrong_location(client,headers):
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/100",headers=headers)
    assert r_get.status_code==200
    data = r_get.json
    assert data["status_code"]==2003
    
new_adress="Place verte 2bis"
def test_patch_get_location(client,headers):
    r_patch=client.patch("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877",json={"address": new_adress},headers=headers)
    assert r_patch.status_code==200 and r_patch.json["status_code"]==1000
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877",headers=headers)
    data["89900877"]["address"]=new_adress
    assert data["89900877"]==r_get.json["data"]
    
def test_patch_unknown_location(client,headers,mock_get):
    r_patch=client.patch("/ocpi/emsp/2.1.1/locations/BE/TEST/101",json={"address": new_adress},headers=headers)
    assert r_patch.status_code==200
    assert r_patch.json["status_code"]==1000
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/101",headers=headers)
    data["89900877"]["id"]="101"
    assert data["89900877"]==r_get.json["data"]
    
def test_patch_wrong_location(client,headers,mock_get):
    r_patch=client.patch("/ocpi/emsp/2.1.1/locations/BE/TEST/102",json={"address": new_adress},headers=headers)
    assert r_patch.json["status_code"]==2003

##EVSE
evse=data["89900877"]["evses"][0]
def test_get_evse(client,headers):
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877/11746794*2",headers=headers)
    assert r_get.status_code==200
    assert evse==r_get.json["data"]

def test_put_evse(client,headers):
    evse_100=deepcopy(evse)
    evse_100["uid"]="100"
    r_put=client.put("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877/100",json=evse_100,headers=headers)
    assert r_put.status_code==200 and r_put.json["status_code"]==1000
    
"""
    
def test_get_wrong_evse(client,headers):
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877/101",headers=headers)
    assert r_get.status_code==200 and r_get.json["status_code"]==2003
    
def test_put_evse_wrong_location(client,headers,mock_get_evse):
    r_put=client.put("/ocpi/emsp/2.1.1/locations/BE/TEST/89828753/1000143862*1",json=data["89828753"]["evses"][0],headers=headers)
    assert r_put.status_code==200
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/89828753/1000143862*1",headers=headers)
    assert data["89828753"]["evses"][0]==r_get.json["data"]
    
def test_patch_get_evse(client,headers):
    r_patch=client.patch("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877/11746794*2",json={"status": "CHARGING"},headers=headers)
    assert r_patch.status_code==200 and r_patch.json["status_code"]==1000
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877/11746794*2",headers=headers)
    evse["status"]="CHARGING"
    assert evse==r_get.json["data"]
    
def test_patch_evse_unknown_evse(client,headers,mock_get_evse):
    r_patch=client.patch("/ocpi/emsp/2.1.1/locations/BE/TEST/101/404",json={"status": "CHARGING"},headers=headers)
    assert r_patch.status_code==200 and r_patch.json["status_code"]==1000
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/101/404",headers=headers)
    assert r_get.json["data"]["status"]=="CHARGING"
    
def test_patch_evse_unknown_location(client,headers,mock_get_evse):
    r_patch=client.patch("/ocpi/emsp/2.1.1/locations/BE/TEST/404/404",json={"status": "CHARGING"},headers=headers)
    assert r_patch.status_code==200 and r_patch.json["status_code"]==1000
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/404/404",headers=headers)
    assert r_get.json["data"]["status"]=="CHARGING"
    
def test_patch_wrong_evse(client,headers,mock_get):
    r_patch=client.patch("/ocpi/emsp/2.1.1/locations/BE/TEST/102",json={"status": "CHARGING"},headers=headers)
    assert r_patch.json["status_code"]==2003


##CONNECTOR    
connector=data["89900877"]["evses"][0]["connectors"][0].copy()
connector["id"]="0"
def test_put_connector(client,headers):
    r_put=client.put("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877/100/0",json=connector,headers=headers)
    assert r_put.status_code==200 and r_put.json["status_code"]==1000

def test_get_wrong_connector(client,headers):
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877/101/9",headers=headers)
    assert r_get.status_code==200 and r_get.json["status_code"]==2003
    
def test_put_connector_unknown_location(client,headers,mock_get_connector):
    r_put=client.put("/ocpi/emsp/2.1.1/locations/BE/TEST/conn404/1000143862*1/1",json=data["89828753"]["evses"][0]["connectors"][0],headers=headers)
    print(r_put.text)
    assert r_put.status_code==200 and r_put.json["status_code"]==1000
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/conn404/1000143862*1/1",headers=headers)
    assert data["89828753"]["evses"][0]["connectors"][0]==r_get.json["data"]
    
def test_put_connector_unknown_evse(client,headers,mock_get_connector):
    assert True

def test_patch_connector_unknown_location(client,headers,mock_get_connector):
    assert True

def test_patch_connector_unknown_evse(client,headers,mock_get_connector):
    assert True
    
def test_put_connector_wrong_location(client,headers,mock_get_connector):
    r_put=client.put("/ocpi/emsp/2.1.1/locations/BE/TEST/wrong/1000143862*1/1",json=data["89828753"]["evses"][0]["connectors"][0],headers=headers)
    assert r_put.status_code==200 and r_put.json["status_code"]==2003
    
def test_put_connector_wrong_evse(client,headers,mock_get_connector):
    assert True

def test_patch_connector_wrong_location(client,headers,mock_get_connector):
    assert True

def test_patch_connector_wrong_evse(client,headers,mock_get_connector):
    assert True

"""
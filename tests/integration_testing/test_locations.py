import json
import sys, os, pathlib
import logging

logging.getLogger('ocpi')

with open(f'{sys.path[0]}/tests/integration_testing/location.json', 'r') as file:
    data = json.load(file)

def test_put_location(client,headers):
    r_put=client.put("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877",json=data["to_send"],headers=headers)
    assert r_put.status_code==200

def test_get_location(client,headers):
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877",headers=headers)
    assert r_get.status_code==200
    assert data["to_get"]==r_get.json["data"]
    
def test_get_wrong_location(client,headers):
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/89900871",headers=headers)
    assert r_get.status_code==200
    data = r_get.json
    assert data["status_code"]==2003
    
def test_patch_location(client,headers):
    new_adress="Place verte 2bis"
    r_patch=client.patch("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877",json={"address": new_adress},headers=headers)
    assert r_patch.status_code==200 #& r_patch.json["status_code"]==1000
    r_get=client.get("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877",headers=headers)
    assert r_get.status_code==200
    data["to_get"]["address"]=new_adress
    assert data["to_get"]==r_get.json["data"]
    
def test_patch_unknown_location(client,headers,server):
    r_put=server.put("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877",json=data["to_send"],headers=headers)
    print(r_put.request)
    assert r_put.status_code==200
    
def test_patch_wrong_location(client,headers):
    assert True
    




import json, sys

with open(f'{sys.path[0]}/tests/integration_testing/sessions.json', 'r') as file:
    data = json.load(file)
    
def test_put_session(client,headers):
    r_put=client.put("/ocpi/emsp/2.1.1/sessions/BE/TEST/BEEQS217609779",json=data["to_put"],headers=headers)
    assert r_put.status_code==200 and r_put.json["status_code"]==1000
    
def test_patch_session(client,headers):
    r_patch=client.patch("/ocpi/emsp/2.1.1/sessions/BE/TEST/BEEQS217609779",json=data["to_patch"],headers=headers)
    assert r_patch.status_code==200 and r_patch.json["status_code"]==1000
    
def test_get_session(client,headers):
    r_get=client.get("/ocpi/emsp/2.1.1/sessions/BE/TEST/BEEQS217609779",headers=headers)
    assert r_get.status_code==200 and r_get.json["status_code"]==1000
    assert r_get.json["data"]==data["to_get"]
    
    
    
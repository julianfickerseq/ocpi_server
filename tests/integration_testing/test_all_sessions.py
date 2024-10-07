
import json, sys
from datetime import datetime, timedelta, timezone

with open(f'{sys.path[0]}/tests/integration_testing/sessions.json', 'r') as file:
    data = json.load(file)
    

def test_get_all_sessions(client,headers):
    for location in ["89343896","90321319"]:
        data["to_put"]["location"]["id"]=location
        for n in range(20):
            data["to_put"]["id"]=f"BE{location}{n}"
            data["to_put"]["start_datetime"]=(datetime(2020,1,1,0,0,0,tzinfo=timezone.utc)+timedelta(days=n-0.1)).isoformat(timespec="seconds").replace("+00:00", "Z")
            data["to_put"]["last_updated"]=(datetime(2020,1,1,0,0,0,tzinfo=timezone.utc)+timedelta(days=n)).isoformat(timespec="seconds").replace("+00:00", "Z")
            r_put=client.put(f"/ocpi/emsp/2.1.1/sessions/BE/TEST/BE{location}{n}",json=data["to_put"],headers=headers)
    r_get=client.get("/ocpi/emsp/2.1.1/sessions/",headers={"Authorization":"Token internaltoken"})
    assert r_get.status_code==200 and r_get.json["status_code"]==1000
    assert len(r_get.json["data"])==40
    assert not r_get.headers.get("Link")

def test_get_sessions_for_user(client):
    r_get=client.get("/ocpi/emsp/2.1.1/sessions/",headers={"Authorization":"Token usertoken"})
    assert r_get.status_code==200 and r_get.json["status_code"]==1000
    assert len(r_get.json["data"])==20
    assert r_get.json["data"][0]["id"][-1]=="0"
    
def test_limit_and_headers_and_offset(client):
    r_get=client.get("/ocpi/emsp/2.1.1/sessions/?limit=10",headers={"Authorization":"Token usertoken"})
    assert len(r_get.json["data"])==10
    assert r_get.json["data"][0]["id"][-1]=="0"
    print(r_get.headers)
    assert r_get.headers.get("Link")=="http://localhost:1234/ocpi/emsp/2.1.1/sessions/?limit=10&offset=10"
    assert r_get.headers.get("X-Total-Count")=="20"
    assert r_get.headers.get("X-Limit")=="10"
    r_get=client.get("/ocpi/emsp/2.1.1/sessions/?limit=10&offset=10",headers={"Authorization":"Token usertoken"})
    assert len(r_get.json["data"])==10
    assert r_get.json["data"][0]["id"][-2:]=="10"
    assert not r_get.headers.get("Link")
    r_get=client.get("/ocpi/emsp/2.1.1/sessions/?limit=10&offset=1",headers={"Authorization":"Token usertoken"})
    assert r_get.headers.get("link")=="http://localhost:1234/ocpi/emsp/2.1.1/sessions/?limit=10&offset=11"

def test_date_from_date_to(client):
    r_get=client.get("/ocpi/emsp/2.1.1/sessions/?date_from=2020-01-01T00:00:00Z&date_to=2020-01-01T00:00:01Z",headers={"Authorization":"Token usertoken"})
    print(r_get.headers)
    assert r_get.status_code==200 and r_get.json["status_code"]==1000
    assert len(r_get.json["data"])==1
    assert r_get.json["data"][0]["id"][-1:]=="0"
    r_get=client.get("/ocpi/emsp/2.1.1/sessions/?limit=1&date_from=2020-01-01T00:00:00Z&date_to=2020-02-01T00:00:01Z",headers={"Authorization":"Token usertoken"})
    assert r_get.headers.get("link")=="http://localhost:1234/ocpi/emsp/2.1.1/sessions/?limit=1&date_from=2020-01-01T00:00:00Z&date_to=2020-02-01T00:00:01Z&offset=1"

    
    
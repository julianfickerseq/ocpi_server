import pytest
import sys, json, os
from main import app
import requests_mock
from pymongo import MongoClient
from copy import deepcopy


CONNECTION_STRING = f'mongodb://{os.environ["MONGO_USER"]}:{os.environ["MONGO_PWD"]}@{os.environ["MONGO_HOST"]}:{os.environ["MONGO_PORT"]}'
mongo = MongoClient(CONNECTION_STRING)
mongo.drop_database('ocpi')

@pytest.fixture()
def client():
    test_client=app.test_client()
    yield test_client

with open(f"{sys.path[0]}/ocpi_creds.json","r") as f:
    cred=json.load(f)
    token=next(iter(cred))
    client_cred=cred[token]

@pytest.fixture()
def headers():
    headers = {
        "Authorization":"Token " + token
    }
    yield headers
    
with open(f'{sys.path[0]}/tests/integration_testing/location.json', 'r') as file:
    data = json.load(file)
    
@pytest.fixture
def mock_get():
    with requests_mock.Mocker() as requests_mocker:
        to_get=data["89900877"]
        to_get["id"]="101"
        requests_mocker.get(
            "http://localhost:5001/api/ocpi/cpo/2.1.1/locations/101",  # Match the target URL.
            request_headers={"Authorization": "Token "+client_cred["client_token"]},
            status_code=200,  # The status code of the response.
            json={
                "status_code":1000,
                "data":to_get,
            } 
        )
        requests_mocker.get(
            "http://localhost:5001/api/ocpi/cpo/2.1.1/locations/102",  # Match the target URL.
            request_headers={"Authorization": "Token "+client_cred["client_token"]},
            status_code=404,  # The status code of the response.
        )
        yield
        
@pytest.fixture
def mock_get_evse():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.get(
            "http://localhost:5001/api/ocpi/cpo/2.1.1/locations/89828753",
            request_headers={"Authorization": "Token "+client_cred["client_token"]},
            status_code=200,
            json={
                "status_code":1000,
                "data":data["89828753"],
            } 
        )
        d_101=data["89828753"].copy()
        d_101["evses"][0]["uid"]="404"
        requests_mocker.get(
            "http://localhost:5001/api/ocpi/cpo/2.1.1/locations/101",
            request_headers={"Authorization": "Token "+client_cred["client_token"]},
            status_code=200,
            json={
                "status_code":1000,
                "data":d_101,
            } 
        )
        d_101["id"]="404"
        requests_mocker.get(
            "http://localhost:5001/api/ocpi/cpo/2.1.1/locations/404",
            request_headers={"Authorization": "Token "+client_cred["client_token"]},
            status_code=200,
            json={
                "status_code":1000,
                "data":d_101,
            } 
        )
        yield
        
@pytest.fixture
def mock_get_connector():
    with requests_mock.Mocker() as requests_mocker:
        conn404=deepcopy(data["89828753"])
        conn404["id"]="conn404"
        requests_mocker.get(
            "http://localhost:5001/api/ocpi/cpo/2.1.1/locations/conn404",
            request_headers={"Authorization": "Token "+client_cred["client_token"]},
            status_code=200,
            json={
                "status_code":1000,
                "data":conn404,
            } 
        )
        unk_conn=deepcopy(data["89828753"])
        unk_conn["evses"][0]["uid"]="404"
        requests_mocker.get(
            "http://localhost:5001/api/ocpi/cpo/2.1.1/locations/101",
            request_headers={"Authorization": "Token "+client_cred["client_token"]},
            status_code=200,
            json={
                "status_code":1000,
                "data":unk_conn,
            } 
        )
        unk_location=deepcopy(data["89828753"])
        unk_location["id"]="unknown_location"
        requests_mocker.get(
            "http://localhost:5001/api/ocpi/cpo/2.1.1/locations/unknown_location",
            request_headers={"Authorization": "Token "+client_cred["client_token"]},
            status_code=200,
            json={
                "status_code":1000,
                "data":unk_location,
            } 
        )
        unk_evse=deepcopy(data["89828753"])
        unk_evse["id"]="404"
        unk_evse["evses"][0]["uid"]="unk_evse"
        requests_mocker.get(
            "http://localhost:5001/api/ocpi/cpo/2.1.1/locations/404",
            request_headers={"Authorization": "Token "+client_cred["client_token"]},
            status_code=200,
            json={
                "status_code":1000,
                "data":unk_evse,
            } 
        )
        yield
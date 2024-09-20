import pytest
import sys, json, os
from main import app
#import tests.integration_testing.mock_flask_app

@pytest.fixture()
def client():
    test_client=app.test_client()
    yield test_client

@pytest.fixture()
def headers():
    with open(f"{sys.path[0]}/ocpi_creds.json","r") as f:
        cred=json.load(f)
        headers = {
            "Authorization":"Token " + next(iter(cred))
        }
    yield headers
    
@pytest.fixture()
def server():
    test_client=app.test_client()
    yield test_client
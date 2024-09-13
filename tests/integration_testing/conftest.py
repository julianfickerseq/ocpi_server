import pytest
import os
from main import app

@pytest.fixture()
def client():
    yield app.test_client()
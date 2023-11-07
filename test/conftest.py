
import pytest
import sys
sys.path.append("..")
from ibooking.app import create_app
import logging



@pytest.fixture()
def app():
    myapp = create_app(is_testing=True)
    return myapp
 
 
@pytest.fixture()
def client(app):
    return app.test_client()
 
 
@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
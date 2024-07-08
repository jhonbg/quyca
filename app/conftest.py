import pytest

from .main import app as create_app

@pytest.fixture(scope="session")
def client():
    create_app.testing = True
    with create_app.test_client() as client:
        yield client

@pytest.fixture(scope="session")
def runner():
    return create_app.test_cli_runner()

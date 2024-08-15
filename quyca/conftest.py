import pytest

from app import create_app

@pytest.fixture(scope="session")
def client():
    create_app.testing = True

    with create_app.test_client() as client:
        yield client

@pytest.fixture(scope="session")
def runner():
    return create_app.test_cli_runner()

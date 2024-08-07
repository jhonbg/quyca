import pytest

from quyca.app import create_app
from quyca.infraestructure.mongo import init_mongo_infraestructure

@pytest.fixture(scope="session")
def client():
    create_app.testing = True
    init_mongo_infraestructure()
    with create_app.test_client() as client:
        yield client

@pytest.fixture(scope="session")
def runner():
    return create_app.test_cli_runner()

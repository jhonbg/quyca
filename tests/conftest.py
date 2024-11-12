from pytest import fixture
from quyca.app import create_app


@fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@fixture()
def client(app):
    client = app.test_client()

    yield client

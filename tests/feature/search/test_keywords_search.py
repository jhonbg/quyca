from pytest import fixture

from quyca import create_app


@fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app


@fixture()
def client(app):
    client = app.test_client()

    yield client


def test_it_can_search_by_institution(client):
    response = client.get('/quyca/search/affiliations/institution?keywords=universidad+de+antioquia')

    assert response.status_code == 200

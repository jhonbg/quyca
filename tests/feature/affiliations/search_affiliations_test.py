def test_search_institutions(client):
    response = client.get(
        f"/app/search/affiliations/institution?keywords=fisica&max=10&page=1"
    )
    assert response.status_code == 200


def test_search_faculties(client):
    response = client.get(
        f"/app/search/affiliations/faculty?keywords=fisica&max=10&page=1"
    )
    assert response.status_code == 200


def test_search_departments(client):
    response = client.get(
        f"/app/search/affiliations/department?keywords=fisica&max=10&page=1"
    )
    assert response.status_code == 200


def test_search_groups(client):
    response = client.get(
        f"/app/search/affiliations/group?keywords=fisica&max=10&page=1"
    )
    assert response.status_code == 200

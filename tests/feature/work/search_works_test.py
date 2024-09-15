def test_search_works(client):
    response = client.get(f"/app/search/works?keywords=quantum&max=10&page=10&sort=citations_desc")
    assert response.status_code == 200


def test_search_works_without_keywords(client):
    response = client.get(f"/app/search/works?max=10&page=10&sort=citations_desc")
    assert response.status_code == 200

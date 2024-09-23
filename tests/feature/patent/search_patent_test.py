def test_search_patents(client) -> None:
    response = client.get(f"/app/search/patents?keywords=quantum&max=10&page=10&sort=citations_desc")
    assert response.status_code == 200


def test_search_patents_without_keywords(client) -> None:
    response = client.get(f"/app/search/patents?max=10&page=10&sort=citations_desc")
    assert response.status_code == 200

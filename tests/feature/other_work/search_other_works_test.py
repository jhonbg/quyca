def test_search_other_works(client) -> None:
    response = client.get(f"/app/search/other_works?keywords=quantum&max=10&page=10&sort=citations_desc")
    assert response.status_code == 200


def test_search_other_works_without_keywords(client) -> None:
    response = client.get(f"/app/search/other_works?max=10&page=10&sort=citations_desc")
    assert response.status_code == 200

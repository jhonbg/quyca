def test_search_projects(client) -> None:
    response = client.get(f"/app/search/projects?keywords=quantum&max=10&page=10&sort=citations_desc")
    assert response.status_code == 200


def test_search_projects_without_keywords(client) -> None:
    response = client.get(f"/app/search/projects?max=10&page=10&sort=citations_desc")
    assert response.status_code == 200

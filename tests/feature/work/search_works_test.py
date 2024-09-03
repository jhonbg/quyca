def test_get_by_id(client):
    response = client.get(f"/app/search/works?keywords=quantum&max=10&page=1")

    assert response.status_code == 200

def test_get_by_id(client):
    response = client.get(
        f"/app/search/person?keywords=diego&max=10&page=1&sort=products_desc"
    )

    assert response.status_code == 200

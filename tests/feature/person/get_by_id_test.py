def test_get_by_id(client):
    response = client.get('/app/person/66b5c3c87102ee7e0fe5eb96')

    assert response.status_code == 200
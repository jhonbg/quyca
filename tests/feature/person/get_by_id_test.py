def test_get_by_id(client):
    response = client.get('app/person/66b583f27102ee7e0fcdbf77')

    assert response.status_code == 200
def test_it_can_search_by_institution(client):
    response = client.get('/quyca/search/affiliations/institution?keywords=universidad+de+antioquia')

    assert response.status_code == 200

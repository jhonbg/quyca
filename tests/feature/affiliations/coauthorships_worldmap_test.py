def test_it_can_send_coauthorships_worldmap(client):
    response = client.get(
        '/app/affiliation/institution/665e0a55aa7c2077adf4d78c/research/products?plot''=collaboration_worldmap'
    )

    assert response.status_code == 200
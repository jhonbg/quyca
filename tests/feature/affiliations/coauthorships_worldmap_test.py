def test_it_can_send_coauthorships_worldmap_by_institution(client):
    response = client.get(
        '/app/affiliation/institution/665e0a55aa7c2077adf4d78c/research/products?plot''=collaboration_worldmap'
    )

    assert response.status_code == 200


def test_it_can_send_coauthorships_worldmap_by_department(client):
    response = client.get(
        '/app/affiliation/department/66b583a37102ee7e0fcda0ca/research/products?plot''=collaboration_worldmap'
    )

    assert response.status_code == 200
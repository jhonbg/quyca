from database.mongo import database

random_affiliation_id = "66b583d97102ee7e0fcda396"


def test_get_institution_by_id(client):
    response = client.get(f"/app/affiliation/institution/{random_affiliation_id}/csv")

    assert response.status_code == 200


def test_get_faculty_by_id(client):
    response = client.get(f"/app/affiliation/faculty/{random_affiliation_id}/csv")

    assert response.status_code == 200


def test_get_department_by_id(client):
    response = client.get(f"/app/affiliation/department/{random_affiliation_id}/csv")

    assert response.status_code == 200


def test_get_group_by_id(client):
    response = client.get(f"/app/affiliation/group/{random_affiliation_id}/csv")

    assert response.status_code == 200

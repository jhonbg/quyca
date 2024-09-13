from database.mongo import database

random_affiliation_id = database["affiliations"].aggregate([{"$sample": {"size": 1}}]).next()["_id"]


def test_get_institution_by_id(client):
    response = client.get(f"/app/affiliation/institution/{random_affiliation_id}")

    assert response.status_code == 200


def test_get_faculty_by_id(client):
    response = client.get(f"/app/affiliation/faculty/{random_affiliation_id}")

    assert response.status_code == 200


def test_get_department_by_id(client):
    response = client.get(f"/app/affiliation/department/{random_affiliation_id}")

    assert response.status_code == 200


def test_get_group_by_id(client):
    response = client.get(f"/app/affiliation/group/{random_affiliation_id}")

    assert response.status_code == 200

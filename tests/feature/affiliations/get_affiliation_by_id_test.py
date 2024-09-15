from database.mongo import database


def test_get_institution_by_id(client):
    random_institution_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "education"}}, {"$sample": {"size": 1}}])
        .next()["_id"]
    )
    response = client.get(f"/app/affiliation/institution/{random_institution_id}")
    assert response.status_code == 200


def test_get_faculty_by_id(client):
    random_faculty_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "faculty"}}, {"$sample": {"size": 1}}])
        .next()["_id"]
    )
    response = client.get(f"/app/affiliation/faculty/{random_faculty_id}")
    assert response.status_code == 200


def test_get_department_by_id(client):
    random_department_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "department"}}, {"$sample": {"size": 1}}])
        .next()["_id"]
    )
    response = client.get(f"/app/affiliation/department/{random_department_id}")
    assert response.status_code == 200


def test_get_group_by_id(client):
    random_group_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "group"}}, {"$sample": {"size": 1}}])
        .next()["_id"]
    )
    response = client.get(f"/app/affiliation/group/{random_group_id}")
    assert response.status_code == 200

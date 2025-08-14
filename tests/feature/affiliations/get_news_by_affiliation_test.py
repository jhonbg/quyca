from quyca.infrastructure.mongo import database


def test_get_news_by_institution(client):
    random_institution_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "Education"}}, {"$sample": {"size": 1}}, {"$project": {"_id": 1}}])
        .next()["_id"]
    )
    response = client.get(f"/app/affiliation/institution/{random_institution_id}/research/news?max=100")
    assert response.status_code == 200


def test_get_news_by_faculty(client):
    random_faculty_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "faculty"}}, {"$sample": {"size": 1}}, {"$project": {"_id": 1}}])
        .next()["_id"]
    )
    response = client.get(f"/app/affiliation/faculty/{random_faculty_id}/research/news?max=100")
    assert response.status_code == 200


def test_get_news_by_department(client):
    random_department_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "department"}}, {"$sample": {"size": 1}}, {"$project": {"_id": 1}}])
        .next()["_id"]
    )
    response = client.get(f"/app/affiliation/department/{random_department_id}/research/news?max=100")
    assert response.status_code == 200


def test_get_news_by_group(client):
    random_group_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "group"}}, {"$sample": {"size": 1}}, {"$project": {"_id": 1}}])
        .next()["_id"]
    )
    response = client.get(f"/app/affiliation/group/{random_group_id}/research/news?max=100")
    assert response.status_code == 200

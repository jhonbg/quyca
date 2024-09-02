import pytest

from database.mongo import database


@pytest.mark.parametrize("_", range(100))
def test_get_csv_works_by_institution(client, _):
    random_institution_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "education"}}, {"$sample": {"size": 1}}])
        .next()["_id"]
    )
    response = client.get(f"/app/affiliation/institution/{random_institution_id}/csv")

    assert response.status_code == 200


@pytest.mark.parametrize("_", range(100))
def test_get_csv_works_by_faculty(client, _):
    random_faculty_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "faculty"}}, {"$sample": {"size": 1}}])
        .next()["_id"]
    )
    response = client.get(f"/app/affiliation/faculty/{random_faculty_id}/csv")

    assert response.status_code == 200


@pytest.mark.parametrize("_", range(100))
def test_get_csv_works_by_department(client, _):
    random_department_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "department"}}, {"$sample": {"size": 1}}])
        .next()["_id"]
    )
    response = client.get(f"/app/affiliation/department/{random_department_id}/csv")

    assert response.status_code == 200


@pytest.mark.parametrize("_", range(100))
def test_get_csv_works_by_group(client, _):
    random_group_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "group"}}, {"$sample": {"size": 1}}])
        .next()["_id"]
    )
    response = client.get(f"/app/affiliation/group/{random_group_id}/csv")

    assert response.status_code == 200

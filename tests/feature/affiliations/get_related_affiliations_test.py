from database.mongo import database

random_affiliation_id = (
    database["affiliations"].aggregate([{"$sample": {"size": 1}}]).next()["_id"]
)


def test_get_institution_by_id(client):
    response = client.get(
        f"/app/affiliation/institution/{random_affiliation_id}/affiliations"
    )

    assert response.status_code == 200

from quyca.database.mongo import database

random_patent_id = database["patents"].aggregate([{"$sample": {"size": 1}}]).next()["_id"]


def test_get_patent_by_id(client):
    response = client.get(f"/app/patent/{random_patent_id}")
    assert response.status_code == 200

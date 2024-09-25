from quyca.infrastructure.mongo import database

random_other_work_id = database["works_misc"].aggregate([{"$sample": {"size": 1}}]).next()["_id"]


def test_get_other_work_by_id(client):
    response = client.get(f"/app/other_work/{random_other_work_id}")
    assert response.status_code == 200

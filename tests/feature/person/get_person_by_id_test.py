from repositories.mongo import database

random_person_id = database["person"].aggregate([{ '$sample': { 'size': 1 } }]).next()["_id"]


def test_get_by_id(client):
    response = client.get(f"/app/person/{random_person_id}")

    assert response.status_code == 200
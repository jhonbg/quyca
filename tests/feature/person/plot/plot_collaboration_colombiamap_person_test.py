from repositories.mongo import database

random_person_id = database["person"].aggregate([{ '$sample': { 'size': 1 } }]).next()["_id"]

def test_it_can_plot_collaboration_colombiamap(client):
    response = client.get(
        f"/app/person/{random_person_id}/research/products?plot=collaboration_colombiamap"
    )

    assert response.status_code == 200



from database.mongo import database

random_person_id = (
    database["person"].aggregate([{"$sample": {"size": 1}}]).next()["_id"]
)


def test_it_can_plot_scienti_rank_by_institution(client):
    response = client.get(
        f"/app/person/{random_person_id}/research/products?plot=scienti_rank"
    )

    assert response.status_code == 200

from random import choice

import pytest
from flask.testing import FlaskClient

from core.logging import get_logger
from core.config import settings
from tests.utils import data as test_data

log = get_logger(__name__)


def test_ping(client: FlaskClient):
    ping = client.get(f"/ping")
    log.debug(ping.json)
    assert ping.status_code == 200
    assert ping.json["ping"] == str(settings.MONGO_URI)


# @pytest.mark.parametrize("name, _type", test_data.affiliations)
# def test_affiliations_search(client: FlaskClient, name: str, _type: str):
#     search = f"{settings.APP_V1_STR}/search"
#     aff = client.get(search + f"/affiliations/{_type}?keywords='{name}'")
#     log.debug(aff.json)
#     assert aff.status_code == 200
#     assert aff.json["data"][0]["name"] == name


@pytest.mark.parametrize("name, _type", test_data.affiliations)
def test_affiliations(client: FlaskClient, name: str, _type: str):
    # get ids from search
    search = f"{settings.APP_V1_STR}/search"
    aff = client.get(search + f"/affiliations/{_type}?keywords='{name}'")
    id = aff.json["data"][0]["id"]
    log.debug(id)
    affiliation = client.get(f"{settings.APP_V1_STR}/affiliation/{_type}/{id}")
    log.debug(affiliation.json)
    data = affiliation.json["data"]
    assert affiliation.status_code == 200
    assert data["id"] == id
    assert isinstance(data["id"], str)
    assert isinstance(data["name"], str)
    assert "affiliations" in data
    assert "external_ids" in data
    assert "external_urls" in data
    assert "products_count" in data
    assert "addresses" in data
    assert "citations_count" in data
    assert isinstance(data["affiliations"], list)
    assert isinstance(data["external_ids"], list)
    assert isinstance(data["external_urls"], list)
    assert isinstance(data["products_count"], int)
    assert isinstance(data["addresses"], list)
    assert isinstance(data["citations_count"], list)

    if _type in ["group", "department", "faculty"]:
        assert len(data["affiliations"]) > 0


@pytest.mark.parametrize(
    "name, _type, sort",
    [
        (*choice(test_data.affiliations), "alphabetical"),
        (*choice(test_data.affiliations), "citations-"),
    ],
)
def test_affiliations_products(client: FlaskClient, name: str, _type: str, sort: str):
    # get ids from search
    search = f"{settings.APP_V1_STR}/search"
    aff = client.get(search + f"/affiliations/{_type}?keywords='{name}'")
    id = aff.json["data"][0]["id"]
    log.debug(id)
    limit = 10
    response = client.get(
        f"{settings.APP_V1_STR}/affiliation/{_type}/{id}/"
        f"research/products?max={limit}&sort={sort}"
    )
    data = response.json["data"]
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == limit
    assert "total_results" in response.json
    assert "count" in response.json
    assert response.json["count"] == limit
    assert "filters" in response.json
    assert "id" in data[0]
    assert "title" in data[0]
    assert "authors" in data[0]
    assert "source" in data[0]
    assert "citations_count" in data[0]
    assert "subjects" in data[0]
    assert "product_type" in data[0]
    assert "year_published" in data[0]
    assert "open_access_status" in data[0]
    assert "external_ids" in data[0]
    assert isinstance(data[0]["authors"], list)
    assert isinstance(data[0]["source"], dict)
    assert isinstance(data[0]["citations_count"], list)
    assert isinstance(data[0]["subjects"], list)
    assert isinstance(data[0]["product_type"], dict)
    assert isinstance(data[0]["year_published"], int)
    assert isinstance(data[0]["open_access_status"], str)
    assert isinstance(data[0]["external_ids"], list)

    if sort == "citations-":
        assert (
            data[0]["citations_count"][0]["count"]
            >= data[-1]["citations_count"][0]["count"]
        )
    if sort == "alphabetical":
        assert data[0]["title"] <= data[-1]["title"]


@pytest.mark.parametrize(
    "plot", [
        "year_type",
        # "type,faculty",
        "type,group",
        "type,department",
        "year_citations",
        "year_apc",
        "year_oa",
        "year_publisher",
        "year_h",
        "year_researcher",
        "year_group",
    ])
def test_affiliation_bar_plots(client: FlaskClient, plot: str):
    name, _type = choice(list(filter(lambda x: x[1] == "faculty", test_data.affiliations)))
    search = f"{settings.APP_V1_STR}/search"
    aff = client.get(search + f"/affiliations/{_type}?keywords='{name}'")
    id = aff.json["data"][0]["id"]
    log.debug(id)
    response = client.get(
            f"{settings.APP_V1_STR}/affiliation/{_type}/{id}/"
            f"research/products?plot={plot}"
        )
    _plot = response.json["plot"]
    log.debug(plot)
    log.debug(_plot)
    assert isinstance(_plot, list)
    assert all(isinstance(x["y"], int) for x in _plot)


@pytest.mark.parametrize(
    "plot", [
        # "citations,faculty",
        "citations,department",
        "citations,group",
        # "products,faculty",
        "products,department",
        "products,group",
        "apc,faculty",
        "apc,department",
        "apc,group",
        "h,faculty",
        "h,department",
        "h,group",
        "products_publisher",
        "products_subject",
        "products_oa",
        "products_sex",
        "products_age",
        "scienti_rank",
        "scimago_rank",
        "published_institution",
    ])
def test_affiliation_pie_plots(client: FlaskClient, plot: str):
    name, _type = choice(list(filter(lambda x: x[1] == "faculty", test_data.affiliations)))
    search = f"{settings.APP_V1_STR}/search"
    aff = client.get(search + f"/affiliations/{_type}?keywords='{name}'")
    id = aff.json["data"][0]["id"]
    log.debug(id)
    response = client.get(
            f"{settings.APP_V1_STR}/affiliation/{_type}/{id}/"
            f"research/products?plot={plot}"
        )
    _plot = response.json["plot"]
    log.debug(plot)
    log.debug(_plot)
    assert isinstance(_plot, list)
    assert "sum" in response.json
    assert isinstance(response.json["sum"], int)
    assert all(isinstance(x["value"], int) or isinstance(x["value"], str) for x in _plot)


# @pytest.mark.parametrize(
#     "name, _type",
#     [choice(list(filter(lambda x: x[1] == "faculty", test_data.affiliations)))],
# )
# def test_affiliation_bars_plots(client: FlaskClient, name: str, _type: str):
#     # get ids from search
#     search = f"{settings.APP_V1_STR}/search"
#     aff = client.get(search + f"/affiliations/{_type}?keywords='{name}'")
#     id = aff.json["data"][0]["id"]
#     log.debug(id)
#     plots = [
#         "title_words",
#         "collaboration_worldmap",
#         "collaboration_colombiamap",
#         "collaboration_network",
#     ]
#     pies_plots = [
#         # "citations,faculty",
#         "citations,department",
#         "citations,group",
#         # "products,faculty",
#         "products,department",
#         "products,group",
#         "apc,faculty",
#         "apc,department",
#         "apc,group",
#         "h,faculty",
#         "h,department",
#         "h,group",
#         "products_publisher",
#         "products_subject",
#         "products_oa",
#         "products_sex",
#         "products_age",
#         "scienti_rank",
#         "scimago_rank",
#         "published_institution",
#     ]
#     for bar_plot in bars_plots:
#         response = client.get(
#             f"{settings.APP_V1_STR}/affiliation/{_type}/{id}/"
#             f"research/products?plot={bar_plot}"
#         )
#         plot = response.json["plot"]
#         log.debug(bar_plot)
#         log.debug(plot)
#         assert isinstance(plot, list)
#         assert all(isinstance(x["y"], int) for x in plot)

#     for pie_plot in pies_plots:
#         response = client.get(
#             f"{settings.APP_V1_STR}/affiliation/{_type}/{id}/"
#             f"research/products?plot={pie_plot}"
#         )
#         plot = response.json["plot"]
#         log.debug(pie_plot)
#         assert isinstance(plot, list)
#         assert "sum" in response.json
#         assert isinstance(response.json["sum"], int)
#         assert all(
#             isinstance(x["value"], int) or isinstance(x["value"], str) for x in plot
#         )

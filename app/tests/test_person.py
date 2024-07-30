from random import choice

import pytest
from flask.testing import FlaskClient

from core.logging import get_logger
from core.config import settings
from tests.utils import data as test_data

log = get_logger(__name__)


@pytest.mark.parametrize("name", test_data.authors)
def test_person(client: FlaskClient, name: str):
    # pytest.skip()
    search = f"{settings.APP_V1_STR}/search"
    person = client.get(search + f"/person?keywords='{name}'")
    log.debug(person.json)
    id = person.json["data"][0]["id"]
    person = client.get(f"{settings.APP_V1_STR}/person/{id}")
    log.debug(person.json)
    data = person.json["data"]
    assert person.status_code == 200
    assert data["id"] == id
    assert isinstance(data["id"], str)
    assert isinstance(data["name"], str)
    assert "affiliations" in data
    assert "external_ids" in data
    assert "products_count" in data
    assert "citations_count" in data
    assert "logo" in data
    assert isinstance(data["affiliations"], list)
    assert isinstance(data["external_ids"], list)
    assert isinstance(data["products_count"], int)
    assert isinstance(data["citations_count"], list)
    assert isinstance(data["logo"], str)


@pytest.mark.parametrize(
    "name, sort",
    [
        (choice(test_data.authors), "alphabetical"),
        (choice(test_data.authors), "citations-"),
    ],
)
def test_authors_products(client: FlaskClient, name: str, sort: str):
    search = f"{settings.APP_V1_STR}/search"
    person = client.get(search + f"/person?keywords='{name}'")
    id = person.json["data"][0]["id"]
    log.debug(id)
    limit = 10
    response = client.get(
        f"{settings.APP_V1_STR}/person/{id}/"
        f"research/products?max={limit}&sort={sort}"
    )
    data = response.json["data"]
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) <= limit
    assert "total_results" in response.json
    assert "count" in response.json
    assert response.json["count"] <= limit
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


@pytest.mark.parametrize("name", [choice(test_data.authors)])
def test_authors_plots(client: FlaskClient, name: str):
    # pytest.skip()
    search = f"{settings.APP_V1_STR}/search"
    aff = client.get(search + f"/person?keywords='{name}'")
    id = aff.json["data"][0]["id"]
    log.debug(id)
    plots = [
        "title_words",
        "collaboration_worldmap",
        "collaboration_colombiamap",
        "collaboration_network",
    ]
    bars_plots = [
        "year_type",
        "year_citations",
        "year_apc",
        "year_oa",
        "year_publisher",
        "year_h",
        "year_researcher",
    ]
    pies_plots = [
        "products_publisher",
        "products_subject",
        "products_database",
        "products_oa",
        "products_age",
        "scienti_rank",
        "scimago_rank",
        "published_institution",
    ]
    for bar_plot in bars_plots:
        response = client.get(
            f"{settings.APP_V1_STR}/person/{id}/"
            f"research/products?plot={bar_plot}"
        )
        plot = response.json["plot"]
        log.debug(bar_plot)
        log.debug(plot)
        assert isinstance(plot, list)
        assert all(isinstance(x["y"], int) for x in plot)

    for pie_plot in pies_plots:
        response = client.get(
            f"{settings.APP_V1_STR}/person/{id}/"
            f"research/products?plot={pie_plot}"
        )
        plot = response.json["plot"]
        log.debug(pie_plot)
        assert isinstance(plot, list)
        assert "sum" in response.json
        assert isinstance(response.json["sum"], int)
        assert all(
            isinstance(x["value"], int) or isinstance(x["value"], str) for x in plot
        )

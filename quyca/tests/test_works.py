import pytest
from flask.testing import FlaskClient

from core import get_logger
from core import settings
from tests.utils import data as test_data

log = get_logger(__name__)


@pytest.mark.parametrize("name", test_data.works)
def test_works(client: FlaskClient, name: str):
    search = f"{settings.APP_V1_STR}/search"
    work = client.get(search + f"/works?keywords='{name}'")
    log.debug(work.json)
    id = work.json["data"][0]["id"]
    work = client.get(f"{settings.APP_V1_STR}/work/{id}")
    log.debug(work.json)
    data = work.json["data"]
    assert work.status_code == 200
    assert data["id"] == id
    assert isinstance(data["id"], str)
    assert isinstance(data["title"], str)
    assert "authors" in data
    assert "source" in data
    assert "citations_count" in data
    assert "subjects" in data
    assert "product_type" in data
    assert "year_published" in data
    assert "open_access_status" in data
    assert "external_ids" in data
    assert "external_urls" in data
    assert "abstract" in data
    assert "language" in data
    assert "volume" in data
    assert "issue" in data
    assert isinstance(data["authors"], list)
    assert isinstance(data["source"], dict)
    assert isinstance(data["citations_count"], int)
    assert isinstance(data["subjects"], list)
    assert isinstance(data["product_type"], dict)
    assert isinstance(data["year_published"], int)
    assert isinstance(data["open_access_status"], str)
    assert isinstance(data["external_ids"], list)
    assert isinstance(data["external_urls"], list)
    assert isinstance(data["abstract"], str)
    assert isinstance(data["language"], str)
    assert isinstance(data["volume"], str)
    assert isinstance(data["issue"], str)

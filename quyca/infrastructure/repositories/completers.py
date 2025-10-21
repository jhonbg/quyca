from quyca.infrastructure.elasticsearch import es_database
from typing import Any, Dict, List
from quyca.config import settings


def person_completer(text: str) -> List[Dict[str, Any]]:
    query = {
        "suggest": {
            "name_suggest": {
                "prefix": text,
                "completion": {"field": "full_name", "size": 5},
            }
        }
    }

    response = es_database.search(index=settings.ES_PERSON_COMPLETER_INDEX, body=query)
    for opt in response["suggest"]["name_suggest"][0]["options"]:
        full_name = ""
        for name in opt["_source"]["full_name"]["input"]:
            if len(full_name) < len(name):
                full_name = name
        opt["full_name"] = full_name
    return response["suggest"]["name_suggest"][0]["options"]


def affiliations_completer(aff_type: str, text: str) -> List[Dict[str, Any]]:
    query = {
        "suggest": {
            "affiliation_suggest": {
                "prefix": text,
                "completion": {"field": "name", "size": 5},
            }
        }
    }

    index = ""
    if aff_type == "institution":
        index = settings.ES_INSTITUTION_COMPLETER_INDEX
    if aff_type == "group":
        index = settings.ES_GROUP_COMPLETER_INDEX
    if aff_type == "department":
        index = settings.ES_DEPARTMENT_COMPLETER_INDEX
    if aff_type == "faculty":
        index = settings.ES_FACULTY_COMPLETER_INDEX
    if not index:
        raise ValueError("Invalid affiliation type")
    if es_database is None:
        raise ValueError("Elasticsearch database is not initialized")

    response = es_database.search(index=index, body=query)
    for opt in response["suggest"]["affiliation_suggest"][0]["options"]:
        name = ""
        if opt["_source"]["full_name"]:
            name = opt["_source"]["full_name"]
        else:
            for _name in opt["_source"]["name"]["input"]:
                if len(name) < len(_name):
                    name = _name
        opt["name"] = name
    return response["suggest"]["affiliation_suggest"][0]["options"]

from infrastructure.elasticsearch import es_database
from typing import Any, Dict, List
from config import settings


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
    return response["suggest"]["name_suggest"][0]["options"]

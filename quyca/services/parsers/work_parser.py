import csv
import io
from typing import Generator

from utils.flatter import get_flat_data


def parse_csv(works: Generator) -> str:
    config = {
        "title": {
            "name": "titulo",
        },
        "authors": {
            "name": "autores",
            "fields": ["full_name"],
            "config": {"full_name": {"name": "full_name"}},
        },
        "lenguage": {"name": "lengua"},
        "citations_count": {
            "name": "veces citado",
            "fields": ["count"],
            "config": {"count": {"name": "count"}},
        },
        "date_published": {
            "name": "fecha publicación",
            "expresion": "datetime.date.fromtimestamp(value).strftime('%Y-%m-%d')",
        },
        "volume": {"name": "volumen"},
        "issue": {"name": "issue"},
        "start_page": {"name": "página inicial"},
        "end_page": {"name": "página final"},
        "year_published": {"name": "año de publicación"},
        "types": {"name": "tipo de producto", "fields": ["type"]},
        "subject_names": {"name": "temas"},
        "doi": {"name": "doi"},
        "source_name": {"name": "revista"},
        "scimago_quartile": {"name": "cuartil de scimago"},
    }
    works = [work.model_dump() for work in works]
    flat_data = get_flat_data(works, config, 1)
    keys = []
    for item in flat_data:
        keys += [key for key in item.keys() if key not in keys]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=keys)
    writer.writeheader()
    writer.writerows(flat_data)
    getvalue = output.getvalue()
    return getvalue

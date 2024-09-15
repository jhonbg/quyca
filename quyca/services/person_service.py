from database.models.base_model import QueryParams
from services.parsers import person_parser
from database.repositories import calculations_repository
from database.repositories import person_repository
from database.repositories import work_repository


def get_person_by_id(person_id: str) -> dict:
    person = person_repository.get_person_by_id(person_id)
    person_calculations = calculations_repository.get_person_calculations(person_id)
    person.citations_count = person_calculations.citations_count
    person.products_count = work_repository.get_works_count_by_person(person_id)
    data = person_parser.parse_person(person)
    return {"data": data}


def search_persons(query_params: QueryParams):
    pipeline_params = {
        "project": [
            "_id",
            "full_name",
            "affiliations",
            "external_ids",
            "citations_count",
            "products_count",
        ]
    }
    persons, total_results = person_repository.search_persons(query_params, pipeline_params)
    persons_list = []
    for person in persons:
        persons_list.append(person)
    data = person_parser.parse_search_result(persons_list)
    return {"data": data, "total_results": total_results}

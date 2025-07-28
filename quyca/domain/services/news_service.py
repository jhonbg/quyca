from domain.models.base_model import QueryParams
from infrastructure.repositories import news_repository
from domain.parsers import news_parser


def get_news_by_person(person_id: str, query_params: QueryParams) -> dict:
    news = news_repository.get_news_by_person(person_id, query_params)
    data = news_parser.parse_news(news)
    total_results = news_repository.news_count_by_person(person_id)
    return {"data": data, "total_results": total_results}

from domain.models.news_model import News


def parse_news(news: News) -> dict:
    return [item.model_dump(mode="json") for item in news]

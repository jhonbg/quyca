from typing import Iterable, List, Dict
from domain.models.news_model import News


def parse_news(news: Iterable[News]) -> List[Dict]:
    return [item.model_dump(mode="json") for item in news]

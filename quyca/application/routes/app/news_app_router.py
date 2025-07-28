from flask import Blueprint, request, jsonify
from domain.models.base_model import QueryParams
from domain.services import news_service

bp = Blueprint("news_app", __name__)


@bp.get("/<person_id>/research/news")
def news_for_person_app(person_id: str):
    qp = QueryParams.model_validate(
        request.args.to_dict(flat=True),
        context={"default_max": 25},
    )
    return jsonify(news_service.get_news_by_person(person_id, qp))

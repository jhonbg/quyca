from flask import Blueprint, request, jsonify, Response
from domain.models.base_model import QueryParams
from domain.services import news_service

bp = Blueprint("news_app", __name__)


@bp.get("/<person_id>/research/news")
def news_for_person_app(person_id: str) -> Response:
    """
    Flask route to retrieve news for a given person ID.

    Validates and parses query parameters, invokes the service layer to get the
    related news data, and returns a JSON response.

    Route:
    ------
    GET /<person_id>/research/news

    Parameters:
    -----------
    person_id : str
        The ID of the person whose news entries are to be retrieved.

    Returns:
    --------
    Response
        Flask JSON response containing news data and total result count.
    """
    qp = QueryParams.model_validate(
        request.args.to_dict(),
        context={"default_max": 25},
    )
    return jsonify(news_service.get_news_by_person(person_id, qp))

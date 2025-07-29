from flask import Blueprint, request, jsonify, Response
from domain.models.base_model import QueryParams
from domain.services import news_service

bp = Blueprint("news", __name__, url_prefix="/person")


@bp.get("/<person_id>/research/news")
def news_for_person(person_id: str) -> Response:
    """
    API route to fetch news entries related to a specific person.

    Parses query parameters, retrieves the corresponding news from the service layer,
    and returns the data as a JSON response.

    Route:
    ------
    GET /person/<person_id>/research/news

    Parameters:
    -----------
    person_id : str
        The ID of the person whose news entries are being requested.

    Returns:
    --------
    Response
        JSON response containing the parsed news data and total count.
    """
    qp = QueryParams.model_validate(request.args.to_dict(), context={"default_max": 25})
    return jsonify(news_service.get_news_by_person(person_id, qp))

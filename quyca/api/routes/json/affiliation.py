import json
from typing import Any

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from quyca.services.affiliation import affiliation_service
from quyca.schemas.affiliation import AffiliationQueryParams

router = Blueprint("affiliation_api_v1", __name__)


@router.route("/<typ>/<id>", methods=["GET"])
@router.route("/<typ>/<id>/<section>", methods=["GET"])
@router.route("/<typ>/<id>/<section>/<tab>", methods=["GET"])
def api_affiliation(
    id: str | None,
    section: str | None = "info",
    tab: str | None = None,
    typ: str | None = None,
):
    """
    @api {get} /affiliation/:typ/:id/:section/:tab get info of an affiliation
    @apiVersion 1.0.0
    @apiName get_affiliation
    @apiGroup Affiliation

    @apiParam {String}    id              The affiliation id.
    @apiParam {String}    typ             The affiliation type.
    @apiParam {String}    [section=info]  The section to get.
                                          use section=info to get general info
                                          use section=research and tab=products to get research products
    @apiParam {String}    [tab]           The tab to get.
    @apiQuery {Number}    [page=1]        Number of page.
    @apiQuery {Number{1-250}}    [max=10]        Number of records to return.
    @apiQuery {String="alphabetical","citations","year"}    [sort=alphabetical]          Sort by field.


    @apiSuccessExample {json} Success-Response:
        HTTP/1.1 200 OK
        {
            "data": [{
                "title": "\"DEPOSITION OF HYPERPHOSPHORYLATED TAU IN CEREBELLUM OF PS1 E280A ALZHEIMER´S DISEASE\"",
                "authors": [],
                "source": {
                    "id": "664b7c85017e10d85a7657b4",
                    "name": "Brain Pathology",
                    "serials": null
                },
                "citations_count": 83,
                "subjects": [

                ],
                "product_type": {
                    "name": "Publicado en revista especializada",
                    "source": "scienti"
                },
                "year_published": 2011,
                "open_access_status": null,
                "external_ids": [
                ],
                "abstract": "",
                "language": "",
                "volume": "21",
                "issue": null,
                "external_urls": [
                ],
                "date_published": null,
                "start_page": "452",
                "end_page": "463",
                "id": "664bf2274847080c5a79959b"
                }],
            "info": {
                "total_products": 1,
                "count": 1,
                "cursor": {
                    "next": "string",
                    "previous": "string"
            }
        }
    """
    try:
        query_params = AffiliationQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    if section == "info":
        return affiliation_service.get_info(id=id, typ=typ, params=query_params)
    if section == "research" and tab == "products":
        return affiliation_service.get_research_products_json(id=id, typ=typ, params=query_params)
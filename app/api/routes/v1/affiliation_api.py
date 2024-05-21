import json
from typing import Any

from flask import Blueprint, request, Response, Request

from services.v1.affiliation_api import affiliation_api_service
from services.work import work_service
from utils.encoder import JsonEncoder
from schemas.general import QueryBase
from core.config import settings

router = Blueprint("affiliation_api_v1", __name__)


def affiliation(
    request: Request,
    *,
    idx: str | None = None,
    section: str | None = "info",
    tab: str | None = None,
    typ: str | None = None,
) -> dict[str, Any] | None:
    result = None
    if section == "info":
        result = affiliation_api_service.get_info(idx)
    elif section == "research":
        if tab == "products":
            plot = request.args.get("plot")
            if plot:
                result = None
            else:
                params = QueryBase(**request.args)
                result = work_service.get_research_products_info_by_affiliation_csv(
                    affiliation_id=idx,
                    affiliation_type=typ,
                    skip=params.skip,
                    limit=params.max,
                    sort=params.sort,
                )
                total = work_service.count_papers(
                    affiliation_id=idx, affiliation_type=typ
                )
                return {
                    "data": result,
                    "info": {
                        "total_products": total,
                        "count": len(result),
                        "cursor": params.get_cursor(
                            path=f"{settings.API_V1_STR}/affiliation/{typ}/{idx}/research/products"
                        ),
                    },
                }
    else:
        result = None
    return {"date": result}


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
    @apiQuery {Number}    [max=10]        Number of records to return.
    @apiQuery {String}    [sort=alphabetical]          Sort by field.

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
    result = affiliation(request, idx=id, section=section, tab=tab, typ=typ)
    if result:
        response = Response(
            response=json.dumps(result, cls=JsonEncoder),
            status=200,
            mimetype="application/json",
        )
    else:
        response = Response(
            response=json.dumps({}, cls=JsonEncoder),
            status=204,
            mimetype="application/json",
        )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

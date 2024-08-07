import json

from flask import Blueprint, request, Response

from quyca.services.v1.person_api import person_api_service
from quyca.services.work import work_service
from quyca.utils.encoder import JsonEncoder
from quyca.schemas.general import QueryBase
from quyca.core.config import settings

router = Blueprint("person_api_v1", __name__)


@router.route("/<id>/<section>/<tab>", methods=["GET"])
def get_person(id: str | None, section: str | None, tab: str | None):
    """
    @api {get} /person/:id/:section/:tab get info of a person
    @apiVersion 1.0.0
    @apiName get_person
    @apiGroup Person

    @apiParam {String}    id              The person id.
    @apiParam {String}    [section]         The section to get info.
    # use section=info to get general info
    # use section=research and tab=products to get research products
    @apiParam {String}    [tab]             The tab to get info.
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
    if section == "info":
        result = person_api_service.get_info(id)
    elif section == "research" and tab == "products":
        params = QueryBase(**request.args)
        works = work_service.get_research_products_by_author_json(
            author_id=id, sort=params.sort, skip=params.skip, limit=params.max
        )
        total = work_service.count_papers(author_id=id)
        result = {
            "data": works,
            "info": {
                "total_products": total,
                "count": len(works),
                "cursor": params.get_cursor(
                    path=f"{settings.API_V1_STR}/person/{id}/research/products", total=total
                ),
            },
        }
    else:
        result = None

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
    return response

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from infraestructure.mongo.utils.session import client
from infraestructure.mongo.repositories.work import WorkRepository
from infraestructure.mongo.repositories.affiliation import AffiliationRepository
from core.config import settings


class SearchAppService:
    def __init__(self):
        self.colav_db = client[settings.MONGO_DATABASE]

    def search_subjects(
        self,
        keywords="",
        max_results=100,
        page=1,
        sort="products",
        direction="descending",
    ):
        search_dict = {}
        var_dict = {"names": 1}
        if keywords:
            search_dict["$text"] = {"$search": keywords}

        var_dict["score"] = {"$meta": "textScore"}
        cursor = self.colav_db["subjects"].find(search_dict, var_dict)

        total = self.colav_db["subjects"].count_documents(search_dict)

        """if sort=="citations":
            cursor.sort([("citations_count",DESCENDING)])
        else:
            cursor.sort([("products_count",DESCENDING)])"""

        if not page:
            page = 1
        else:
            try:
                page = int(page)
            except:
                print("Could not convert end page to int")
                return None
        if not max_results:
            max_results = 100
        else:
            try:
                max_results = int(max_results)
            except:
                print("Could not convert end max to int")
                return None
        if max_results > 250:
            max_results = 250

        cursor = cursor.skip(max_results * (page - 1)).limit(max_results)

        if cursor:
            subjects_list = []
            for subject in cursor:
                name = ""
                for n in subject["names"]:
                    if n["lang"] == "es":
                        name = n["name"]
                        break
                    elif n["lang"] == "en":
                        name = n["name"]
                entry = {
                    "name": name,
                    "id": subject["_id"],
                    # "products_count":subject["products_count"],
                    # "citations_count":subject["citations_count"]
                }
                subjects_list.append(entry)

            return {
                "total_results": total,
                "count": len(subjects_list),
                "page": page,
                "filters": {},
                "data": subjects_list,
            }

        else:
            return None

    def search_person(
        self,
        keywords="",
        institutions="",
        groups="",
        country="",
        max_results=100,
        page=1,
        sort="citations",
    ):
        search_dict = {"external_ids": {"$ne": []}}
        var_dict = {
            "full_name": 1,
            "external_ids": 1,
            "affiliations": 1,
            "products_count": 1,
            "citations_count": 1,
        }
        aff_list = []
        if institutions:
            aff_list.extend([ObjectId(inst) for inst in institutions.split()])
        if groups:
            aff_list.extend([ObjectId(grp) for grp in groups.split()])
        if len(aff_list) != 0:
            search_dict["affiliations.id"] = {"$in": aff_list}

        if keywords:
            search_dict["$text"] = {"$search": keywords}
            filter_cursor = (
                self.colav_db["person"]
                .find(
                    {"$text": {"$search": keywords}, "external_ids": {"$ne": []}},
                    {"score": {"$meta": "textScore"}},
                )
                .sort([("score", {"$meta": "textScore"})])
            )
        else:
            filter_cursor = self.colav_db["person"].find({"external_ids": {"$ne": []}})

        if keywords:
            var_dict["score"] = {"$meta": "textScore"}

        cursor = self.colav_db["person"].find(search_dict, var_dict)

        # institution_filters = []
        # group_filters = []
        # institution_ids = []
        # groups_ids = []

        # for author in filter_cursor:
        #     if "affiliations" in author.keys():
        #         if len(author["affiliations"]) > 0:
        #             for aff in author["affiliations"]:
        #                 if "types" in aff.keys():
        #                     for typ in aff["types"]:
        #                         if typ["type"] == "group":
        #                             if not str(aff["id"]) in groups_ids:
        #                                 groups_ids.append(str(aff["id"]))
        #                                 group_filters.append(
        #                                     {"id": str(aff["id"]), "name": aff["name"]}
        #                                 )
        #                         else:
        #                             if not str(aff["id"]) in institution_ids:
        #                                 institution_ids.append(str(aff["id"]))
        #                                 entry = {
        #                                     "id": str(aff["id"]),
        #                                     "name": aff["name"],
        #                                 }
        #                                 institution_filters.append(entry)
        if keywords:
            cursor.sort([("score", {"$meta": "textScore"})])

        total = self.colav_db["person"].count_documents(search_dict)
        if not page:
            page = 1
        else:
            try:
                page = int(page)
            except:
                # print("Could not convert end page to int")
                return None
        if not max_results:
            max_results = 100
        else:
            try:
                max_results = int(max_results)
            except:
                # print("Could not convert end max to int")
                return None

        cursor = cursor.skip(max_results * (page - 1)).limit(max_results)

        if cursor:
            author_list = []
            keywords = []
            # group_name = ""
            # group_id = ""
            for author in cursor:
                if "score" in author:
                    del author["score"]
                ext_ids = []
                for ext in author["external_ids"]:
                    if ext["source"] in [
                        "Cédula de Ciudadanía",
                        "Cédula de Extranjería",
                        "Passport",
                    ]:
                        continue
                    ext_ids.append(ext)
                author["external_ids"] = ext_ids
                author["products_count"] = WorkRepository.count_papers_by_author(
                    author_id=author["_id"]
                )
                author["citations_count"] = WorkRepository.count_citations_by_author(
                    author_id=author["_id"]
                )
                author_list.append(author)

            return {
                "total_results": total,
                "count": len(author_list),
                "page": page,
                # "filters":{"institutions":institution_filters,"groups":group_filters},
                "data": author_list,
            }
        else:
            return None

    def search_affiliations(
        self, keywords="", max_results=100, page=1, sort="citations", aff_type=None
    ):
        search_dict = {}
        var_dict = {
            "names": 1,
            "relations": 1,
            "addresses": 1,
            "external_ids": 1,
            "external_urls": 1,
            "types": 1,
            "relations": 1,
        }
        if aff_type:
            if aff_type == "institution":
                search_dict = {"types.type": {"$in": settings.institutions}}
            else:
                search_dict = {"types.type": aff_type}
        if keywords:
            search_dict["$text"] = {"$search": keywords}
            var_dict["score"] = {"$meta": "textScore"}

        cursor = self.colav_db["affiliations"].find(search_dict, var_dict)

        if keywords:
            cursor.sort([("score", {"$meta": "textScore"})])

        total = self.colav_db["affiliations"].count_documents(search_dict)

        if not page:
            page = 1
        else:
            try:
                page = int(page)
            except:
                print("Could not convert end page to int")
                return None
        if not max_results:
            max_results = 100
        else:
            try:
                max_results = int(max_results)
            except:
                print("Could not convert end max to int")
                return None

        cursor = cursor.skip(max_results * (page - 1)).limit(max_results)
        if cursor:
            affiliation_list = []
            for affiliation in cursor:
                entry = affiliation.copy()
                del entry["names"]
                del entry["relations"]
                entry["relations"] = []
                name = affiliation["names"][0]["name"]
                entry["affiliations"] = AffiliationRepository.upside_relations(affiliation["relations"], aff_type)
                for n in affiliation["names"]:
                    if n["lang"] == "es":
                        name = n["name"]
                        break
                    if n["lang"] == "en":
                        name = n["name"]

                entry["name"] = name
                entry["logo"] = ""
                for ext in affiliation["external_urls"]:
                    if ext["source"] == "logo":
                        entry["logo"] = ext["url"]
                        affiliation["external_urls"].remove(ext)
                # count_products and citations
                aff_type = entry["types"][0]["type"]

                entry["products_count"] = WorkRepository.count_papers(
                    affiliation_id=entry["_id"], affiliation_type=aff_type
                )

                # count citations
                entry["citations_count"] = WorkRepository.count_citations(
                    affiliation_id=entry["_id"], affiliation_type=aff_type
                )

                affiliation_list.append(entry)

            return {
                "total_results": total,
                "data": affiliation_list,
            }
        else:
            return None

    def search_work(
        self,
        keywords="",
        max_results=100,
        page=1,
        start_year=None,
        end_year=None,
        sort="citations",
        direction="descending",
        tipo=None,
        institutions=None,
        groups=None,
    ):
        papers = []
        total = 0
        open_access = []
        if start_year:
            try:
                start_year = int(start_year)
            except:
                print("Could not convert start year to int")
                return None
        if end_year:
            try:
                end_year = int(end_year)
            except:
                print("Could not convert end year to int")
                return None

        if tipo:
            search_dict = {"types.type": tipo}
        else:
            search_dict = {}
        if start_year or end_year:
            search_dict["year_published"] = {}
        if start_year:
            search_dict["year_published"]["$gte"] = start_year
        if end_year:
            search_dict["year_published"]["$lte"] = end_year

        aff_list = []
        if institutions:
            aff_list.extend([ObjectId(inst) for inst in institutions.split()])
        if groups:
            aff_list.extend([ObjectId(grp) for grp in groups.split()])
        if len(aff_list) != 0:
            search_dict["authors.affiliations.id"] = {"$in": aff_list}
        if keywords:
            search_dict["$text"] = {"$search": keywords}

        cursor = self.colav_db["works"].find(search_dict)

        total = self.colav_db["works"].count_documents(search_dict)
        if not page:
            page = 1
        else:
            try:
                page = int(page)
            except:
                print("Could not convert end page to int")
                return None
        if not max_results:
            max_results = 100
        else:
            try:
                max_results = int(max_results)
            except:
                print("Could not convert end max to int")
                return None

        if sort == "citations" and direction == "ascending":
            cursor.sort([("citations_count.count", ASCENDING)])
        elif sort == "citations" and direction == "descending":
            cursor.sort([("citations_count.count", DESCENDING)])
        elif sort == "year" and direction == "ascending":
            cursor.sort([("year_published", ASCENDING)])
        elif sort == "year" and direction == "descending":
            cursor.sort([("year_published", DESCENDING)])

        cursor = cursor.skip(max_results * (page - 1)).limit(max_results)

        if cursor:
            for paper in cursor:
                entry = {
                    "id": paper["_id"],
                    "title": paper["titles"][0]["title"],
                    "authors": [],
                    "source": "",
                    "open_access_status": (
                        paper["bibliographic_info"]["open_access_status"]
                        if "open_access_status" in paper["bibliographic_info"]
                        else ""
                    ),
                    "year_published": paper["year_published"],
                    "citations_count": (
                        paper["citations_count"]
                        if "citations_count" in paper.keys()
                        else 0
                    ),
                    "subjects": [],
                }

                for subs in paper["subjects"]:
                    if subs["source"] == "openalex":
                        for sub in subs["subjects"]:
                            name = sub.get("name", "No name in db")
                            entry["subjects"].append({"name": name, "id": sub["id"]})
                        break

                if "source" in paper.keys():
                    if "id" in paper["source"].keys():
                        if "name" in paper["source"].keys():
                            entry["source"] = {
                                "name": paper["source"]["name"],
                                "id": paper["source"]["id"],
                            }
                        elif "names" in paper["source"].keys():
                            entry["source"] = {
                                "name": paper["source"]["names"][0]["name"],
                                "id": paper["source"]["id"],
                            }

                authors = []
                for author in paper["authors"]:
                    au_entry = author.copy()
                    if not "affiliations" in au_entry.keys():
                        au_entry["affiliations"] = []
                    author_db = None
                    if "id" in author.keys():
                        if author["id"] == "":
                            continue
                        author_db = self.colav_db["person"].find_one(
                            {"_id": author["id"]}
                        )
                    else:
                        continue
                    if author_db:
                        au_entry = {
                            "id": author_db["_id"],
                            "full_name": author_db["full_name"],
                            "external_ids": [
                                ext
                                for ext in author_db["external_ids"]
                                if not ext["source"]
                                in [
                                    "Cédula de Ciudadanía",
                                    "Cédula de Extranjería",
                                    "Passport",
                                ]
                            ],
                        }
                    affiliations = []
                    aff_ids = []
                    aff_types = []
                    for aff in author["affiliations"]:
                        if "id" in aff.keys():
                            if aff["id"]:
                                aff_db = self.colav_db["affiliations"].find_one(
                                    {"_id": aff["id"]}
                                )
                                if aff_db:
                                    aff_ids.append(aff["id"])
                                    aff_entry = {"id": aff_db["_id"], "name": ""}
                                    if author_db:
                                        for aff_au in author_db["affiliations"]:
                                            if aff_au["id"] == aff["id"]:
                                                if "start_date" in aff_au.keys():
                                                    aff_entry["start_date"] = aff_au[
                                                        "start_date"
                                                    ]
                                                if "end_date" in aff_au.keys():
                                                    aff_entry["end_date"] = aff_au[
                                                        "end_date"
                                                    ]
                                                break
                                    name = aff_db["names"][0]["name"]
                                    lang = ""
                                    for n in aff_db["names"]:
                                        if "lang" in n.keys():
                                            if n["lang"] == "es":
                                                name = n["name"]
                                                lang = n["lang"]
                                                break
                                            elif n["lang"] == "en":
                                                name = n["name"]
                                                lang = n["lang"]
                                    aff["name"] = name
                                    if "types" in aff.keys():
                                        for typ in aff["types"]:
                                            if "type" in typ.keys():
                                                if not typ["type"] in aff_types:
                                                    aff_types.append(typ["type"])
                                    affiliations.append(aff)
                    if author_db:
                        for aff in author_db["affiliations"]:
                            if aff["id"] in aff_ids:
                                continue
                            if aff["id"]:
                                aff_db = self.colav_db["affiliations"].find_one(
                                    {"_id": aff["id"]}
                                )
                                inst_already = False
                                if aff_db:
                                    if "types" in aff_db.keys():
                                        for typ in aff_db["types"]:
                                            if "type" in typ.keys():
                                                if typ["type"] in aff_types:
                                                    inst_already = True
                                    if inst_already:
                                        continue
                                    aff_ids.append(aff["id"])
                                    aff_entry = {"id": aff_db["_id"], "name": ""}
                                    name = aff_db["names"][0]["name"]
                                    lang = ""
                                    for n in aff_db["names"]:
                                        if "lang" in n.keys():
                                            if n["lang"] == "es":
                                                name = n["name"]
                                                lang = n["lang"]
                                                break
                                            elif n["lang"] == "en":
                                                name = n["name"]
                                                lang = n["lang"]
                                    aff["name"] = name
                                    affiliations.append(aff)
                    au_entry["affiliations"] = affiliations
                    authors.append(au_entry)
                entry["authors"] = authors
                papers.append(entry)

            return {
                "data": papers,
                "count": len(papers),
                "page": page,
                "total_results": total,
            }
        else:
            return None


search_app_service = SearchAppService()

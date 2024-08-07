from bson import ObjectId

from quyca.infraestructure.mongo.utils.session import client
from quyca.core.config import settings


class WorkAppService:
    def __init__(self):
        self.colav_db = client[settings.MONGO_INITDB_DATABASE]
        self.impactu_db = client[settings.MONGO_IMPACTU_DB]

    def get_info(self, idx):
        document = self.colav_db["works"].find_one({"_id": ObjectId(idx)})
        if document:
            entry = {
                "id": document["_id"],
                "title": document["titles"][0]["title"],
                "abstract": document.get("abstract", ""),
                "source": {},
                "year_published": document["year_published"],
                "language": "",
                "volume": "",
                "issue": "",
                "authors": [],
                "policies": {},
                "open_access_status": "",
                "citations_count": 0,
                "external_ids": [],
                "external_urls": document["external_urls"],
            }
            if "language" in document.keys():
                entry["language"] = (
                    document["languages"][0] if len(document["languages"]) > 0 else ""
                )
            if "bibliographic_info" in document.keys():
                if "volume" in document["bibliographic_info"].keys():
                    entry["volume"] = document["bibliographic_info"]["volume"]
                if "issue" in document["bibliographic_info"].keys():
                    entry["issue"] = document["bibliographic_info"]["issue"]
                if "open_access_status" in document["bibliographic_info"].keys():
                    entry["open_access_status"] = document["bibliographic_info"][
                        "open_access_status"
                    ]
            index_list = []
            if "citations_count" in document.keys():
                for cite in document["citations_count"]:
                    if cite["source"] == "scholar":
                        entry["citations_count"] = cite["count"]
                        break
                    elif cite["source"] == "openalex":
                        entry["citations_count"] = cite["count"]
            if "source" in document.keys() and document["source"].get("id", None):
                source = self.colav_db["sources"].find_one(
                    {"_id": document["source"]["id"]}
                )
                entry_source = {
                    "name": (
                        document["source"]["names"][0]
                        if "names" in document["source"].keys()
                        else document["source"]["name"]
                    ),
                    "serials": {},
                }
                for serial in source.get("external_ids", []):
                    if not serial["source"] in entry_source["serials"].keys():
                        entry_source["serials"][serial["source"]] = serial["id"]
                entry["source"] = entry_source

            authors = []
            for author in document["authors"]:
                au_entry = author.copy()
                if not "affiliations" in au_entry.keys():
                    au_entry["affiliations"] = []
                author_db = None
                if "id" in author.keys():
                    if author["id"] == "":
                        continue
                    author_db = self.colav_db["person"].find_one({"_id": author["id"]})
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

            for ext in document["external_ids"]:
                if ext["source"] == "doi":
                    entry["external_ids"].append(
                        {
                            "id": ext["id"],
                            "source": "doi",
                            "url": "https://doi.org/" + ext["id"],
                        }
                    )
                if ext["source"] == "lens":
                    entry["external_ids"].append(
                        {
                            "id": ext["id"],
                            "source": "lens",
                            "url": "https://www.lens.org/lens/scholar/article/"
                            + ext["id"],
                        }
                    )
                if ext["source"] == "scholar":
                    entry["external_ids"].append(
                        {
                            "id": ext["id"],
                            "source": "scholar",
                            "url": "https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=info%3A"
                            + ext["id"]
                            + "%3Ascholar.google.com",
                        }
                    )
                if ext["source"] == "minciencias":
                    entry["external_ids"].append(
                        {"id": ext["id"], "source": "minciencias", "url": ""}
                    )

            return {"data": entry, "filters": {}}
        else:
            return None


work_app_service = WorkAppService()

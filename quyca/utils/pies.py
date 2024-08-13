import datetime
from typing import Iterable, Callable, Any
from collections import Counter
import functools

from utils.cpi import inflate
from currency_converter import CurrencyConverter

from utils.hindex import hindex
from protocols.mongo.models.work import Work, SubjectEmbedded, Updated
from protocols.mongo.models.general import CitationsCount
from protocols.mongo.models.source import Publisher, Source, Ranking
from schemas.source import APC


class pies:
    def __init__(self):
        pass

    def get_percentage(func: Callable[[Any], list[dict[str, str | int]]]):
        @functools.wraps(func)
        def wrapper(
            self, *args, **kwargs
        ) -> dict[str, list[dict[str, str | int]] | int]:
            data = func(self, *args, **kwargs)
            total = sum([i["value"] for i in data])
            for i in data:
                i["percentage"] = round((i["value"] / total) * 100, 2) if total else 0
            return {"plot": data, "sum": total}

        return wrapper

    # Accumulated citations for each faculty department or group
    @get_percentage
    def citations_by_affiliation(
        self, data: dict[str, list[CitationsCount]]
    ) -> list[dict[str, str | int]]:
        results = {}
        for name, citations in data.items():
            for count in citations:
                c = 0
                if count.source == "scholar":
                    c = count.count
                    break
                elif count.source == "openalex":
                    c = count.count
                    break
            results[name] = c

        result_list = []
        for idx, value in results.items():
            result_list.append({"name": idx, "value": value})
        return result_list

    # Accumulated papers for each faculty department or group
    @get_percentage
    def products_by_affiliation(
        self, data: dict[str, int], total_works=0
    ) -> list[dict[str, str | int]]:
        result_list = []
        for idx, value in data.items():
            result_list.append({"name": idx, "value": value})
        result_list.append(
            {"name": "Sin información", "value": total_works - sum(data.values())}
        )
        return result_list

    # APC cost for each faculty department or group
    @get_percentage
    def apc_by_affiliation(
        self, data: Iterable[Source], base_year
    ) -> list[dict[str, str | int]]:
        c = CurrencyConverter()
        now = datetime.date.today()
        result = {}
        for source in data:
            apc = source.apc
            value = 0
            if apc.currency == "USD":
                raw_value = apc.charges
                value = inflate(
                    raw_value,
                    apc.year_published,
                    to=max(base_year, apc.year_published),
                )
            else:
                try:
                    raw_value = c.convert(apc.charges, apc.currency, "USD")
                    value = inflate(
                        raw_value,
                        apc.year_published,
                        to=max(base_year, apc.year_published),
                    )
                except Exception as e:
                    # print("Could not convert currency with error: ",e)
                    value = 0
            if value:
                name = source.affiliation_names[0].name
                if name not in result.keys():
                    result[name] = value
                else:
                    result[name] += value
        result_list = []
        for idx, value in result.items():
            result_list.append({"name": idx, "value": int(value)})
        return result_list

    # H index for each faculty department or group
    @get_percentage
    def hindex_by_affiliation(
        self, data: dict[str, Iterable[int]]
    ) -> list[dict[str, str | int]]:
        result_list = []
        for idx, value in data.items():
            result_list.append({"name": idx, "value": hindex(value)})
        return result_list

    # Ammount of papers per publisher
    @get_percentage
    def products_by_publisher(self, data: Iterable[str]) -> list[dict[str, str | int]]:
        results = Counter(data)
        result_list = []
        for idx, value in results.items():
            result_list += [{"name": idx, "value": value}]
        return result_list

    # ammount of papers per openalex subject
    @get_percentage
    def products_by_subject(
        self, data: Iterable[SubjectEmbedded]
    ) -> list[dict[str, str | int]]:
        results = Counter(sub.name for sub in data)
        result_list = []
        for name, count in results.items():
            result_list.append({"name": name, "value": count})
        return result_list

    # Ammount of papers per database
    @get_percentage
    def products_by_database(
        self, data: Iterable[Updated]
    ) -> list[dict[str, str | int]]:
        results = Counter(up.source for up in data)
        result_list = []
        for name, count in results.items():
            result_list.append({"name": name, "value": count})
        return result_list

    # Ammount of papers per open access status
    @get_percentage
    def products_by_open_access_status(
        self, data: Iterable[str]
    ) -> list[dict[str, str | int]]:
        results = Counter(data)
        result_list = []
        for name, count in results.items():
            result_list.append({"name": name, "value": count})
        return result_list

    # Ammount of papers per author sex
    @get_percentage
    def products_by_sex(self, data) -> list[dict[str, str | int]]:
        return data

    # Ammount of papers per author age intervals 14-26 años, 27-59 años 60 años en adelante
    @get_percentage
    def products_by_age(self, data) -> list[dict[str, str | int]]:
        ranges = {"14-26": (14, 26), "27-59": (27, 59), "60+": (60, 999)}
        results = {"14-26": 0, "27-59": 0, "60+": 0, "Sin información": 0}
        for work in data:
            if (
                not work["birthdate"]
                or work["birthdate"] == -1
                or not work["work"]["date_published"]
            ):
                results["Sin información"] += 1
                continue
            if work["birthdate"]:
                birthdate = datetime.datetime.fromtimestamp(
                    work["birthdate"]
                ).year
                date_published = datetime.datetime.fromtimestamp(
                    work["work"]["date_published"]
                ).year
                age = date_published - birthdate
                for name, (date_low, date_high) in ranges.items():
                    if date_low <= age <= date_high:
                        results[name] += 1
                        break
        result_list = []
        for idx, value in results.items():
            result_list.append({"name": idx, "value": value})
        return result_list

    # Ammount of papers per scienti rank
    @get_percentage
    def products_by_scienti_rank(
        self, data: Iterable[Ranking], total_works=0
    ) -> list[dict[str, str | int]]:
        scienti_rank = filter(
            lambda x: x.source == "scienti"
            and x.rank
            and x.rank.split("_")[-1] in ["A", "A1", "B", "C", "D"],
            data,
        )
        results = Counter(map(lambda x: x.rank.split("_")[-1], scienti_rank))
        result_list = []
        for name, count in results.items():
            result_list.append({"name": name, "value": count})
        result_list.append(
            {"name": "Sin información", "value": total_works - sum(results.values())}
        )
        return result_list

    # Ammount of papers per journal on scimago
    @get_percentage
    def products_by_scimago_rank(
        self, data: Iterable[Ranking]
    ) -> list[dict[str, str | int]]:
        results = {}
        scimago_rank = filter(lambda x: x.source == "scimago Best Quartile", data)
        results = Counter(map(lambda x: x.rank, scimago_rank))
        result_list = []
        for idx, value in results.items():
            result_list.append({"name": idx, "value": value})
        return result_list

    # Ammmount of papers published on a journal of the same institution
    @get_percentage
    def products_editorial_same_institution(
        self, data: Iterable[Source], institution
    ) -> list[dict[str, str | int]]:
        results = {"same": 0, "different": 0, "Sin información": 0}
        names = list(set([n["name"].lower() for n in institution["names"]]))

        for source in data:
            if (
                not source.publisher
                or not source.publisher.name
                or not isinstance(source.publisher.name, str)
            ):
                results["Sin información"] += 1
                continue
            if source.publisher.name.lower() in names:
                results["same"] += 1
            else:
                results["different"] += 1
        result_list = []
        for idx, value in results.items():
            result_list.append({"name": idx, "value": value})
        return result_list

    @get_percentage
    def title_words(
        self, data: list[dict[str, str | int]]
    ) -> list[dict[str, str | int]]:
        return data

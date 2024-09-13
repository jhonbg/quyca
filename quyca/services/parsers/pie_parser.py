from functools import wraps
from datetime import datetime
from typing import Callable, Generator, Iterable
from collections import Counter
from currency_converter import CurrencyConverter

from database.models.base_model import CitationsCount
from utils.cpi import inflate
from utils.hindex import hindex


def get_percentage(func: Callable[..., list[dict[str, str | int]]]):
    @wraps(func)
    def wrapper(*args, **kwargs) -> dict[str, list[dict[str, str | int | float]] | int]:
        data = func(*args, **kwargs)
        total = sum(item["value"] for item in data)
        for item in data:
            item["percentage"] = round(item["value"] / total * 100, 2) if total else 0
        return {"plot": data, "sum": total}

    return wrapper


@get_percentage
def get_citations_by_affiliation(
    data: dict[str, list[CitationsCount]]
) -> list[dict[str, str | int]]:
    counter = 0
    results = {}
    for name, citations in data.items():
        for count in citations:
            counter = 0
            if count.source == "scholar":
                counter = count.count
                break
            elif count.source == "openalex":
                counter = count.count
                break
        results[name] = counter
    plot = []
    for name, value in results.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def get_apc_by_sources(sources: Generator, base_year) -> list:
    currency_converter = CurrencyConverter()
    result = {}
    for source in sources:
        apc = source.apc
        if apc.currency == "USD":
            raw_value = apc.charges
            value = inflate(raw_value, apc.year_published, to=max(base_year, apc.year_published))
        else:
            try:
                raw_value = currency_converter.convert(apc.charges, apc.currency, "USD")
                value = inflate(
                    raw_value, apc.year_published, to=max(base_year, apc.year_published)
                )
            except Exception:
                value = 0
        if value and (name := source.affiliation_names[0].name):
            if name not in result.keys():
                result[name] = value
            else:
                result[name] += value
    plot = []
    for name, value in result.items():
        plot.append({"name": name, "value": int(value)})
    return plot


@get_percentage
def get_h_by_affiliation(data: dict) -> list:
    plot = []
    for idx, value in data.items():
        plot.append({"name": idx, "value": hindex(value)})
    return plot


@get_percentage
def get_products_by_publisher(data: Iterable[str]) -> list:
    results = Counter(data)
    plot = []
    for name, value in results.items():
        plot += [{"name": name, "value": value}]
    return plot


@get_percentage
def get_products_by_subject(data: Iterable) -> list:
    results = Counter(sub.name for sub in data)
    plot = []
    for name, value in results.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def get_products_by_database(data: Iterable) -> list:
    results = Counter(up.source for up in data)
    plot = []
    for name, value in results.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def get_products_by_open_access(data: Iterable) -> list:
    results = Counter(data)
    plot = []
    for name, value in results.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def get_products_by_age(works: Iterable) -> list:
    ranges = {"14-26": (14, 26), "27-59": (27, 59), "60+": (60, 999)}
    results = {"14-26": 0, "27-59": 0, "60+": 0, "Sin información": 0}
    for work in works:
        if not work["birthdate"] or work["birthdate"] == -1 or not work["work"]["date_published"]:
            results["Sin información"] += 1
            continue
        if work["birthdate"]:
            birthdate = datetime.fromtimestamp(work["birthdate"]).year
            date_published = datetime.fromtimestamp(work["work"]["date_published"]).year
            age = date_published - birthdate
            for name, (date_low, date_high) in ranges.items():
                if date_low <= age <= date_high:
                    results[name] += 1
                    break
    plot = []
    for name, value in results.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def get_articles_by_scienti_category(data: Iterable, total_works=0) -> list:
    scienti_category = filter(
        lambda x: x.source == "scienti"
        and x.rank
        and x.rank.split("_")[-1] in ["A", "A1", "B", "C", "D"],
        data,
    )
    results = Counter(map(lambda x: x.rank.split("_")[-1], scienti_category))
    plot = []
    for name, value in results.items():
        plot.append({"name": name, "value": value})
    plot.append({"name": "Sin información", "value": total_works - sum(results.values())})
    return plot


@get_percentage
def get_articles_by_scimago_quartile(data: list, total_results: int) -> list:
    plot = [{"name": "Sin información", "value": total_results - len(data)}]
    results = Counter(data)
    for name, value in results.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def get_products_by_same_institution(sources: Iterable, institution) -> list:
    results = {"same": 0, "different": 0, "Sin información": 0}
    names = []
    if institution:
        names = list(set([name["name"].lower() for name in institution["names"]]))
    for source in sources:
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
    plot = []
    for name, value in results.items():
        plot.append({"name": name, "value": value})
    return plot

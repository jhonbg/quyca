from functools import wraps
from datetime import datetime
from itertools import chain
from typing import Callable, Iterable, Generator
from collections import Counter
from currency_converter import CurrencyConverter
from pymongo.command_cursor import CommandCursor

from utils.hindex import get_works_h_index_by_scholar_citations


def get_percentage(func: Callable[..., list]) -> Callable[..., dict]:
    @wraps(func)
    def wrapper(*args: Iterable, **kwargs: dict) -> dict:
        data = func(*args, **kwargs)
        total = sum(item["value"] for item in data)
        for item in data:
            item["percentage"] = round(item["value"] / total * 100, 2) if total else 0
        return {"plot": data, "sum": total}

    return wrapper


@get_percentage
def parse_citations_by_affiliations(data: CommandCursor) -> list:
    plot: list = []
    for item in data:
        citations_count = item.get("citations_count", {})
        openalex_citations_count: dict = next(filter(lambda x: x["source"] == "openalex", citations_count), {})
        plot.append({"name": item.get("name", "No name"), "value": openalex_citations_count.get("count", 0)})
    return plot


@get_percentage
def parse_apc_expenses_by_affiliations(data: CommandCursor) -> list:
    CurrencyConverter()
    result: dict = {}
    plot = []
    for name, value in result.items():
        plot.append({"name": name, "value": int(value)})
    return plot


@get_percentage
def parse_h_index_by_affiliation(data: CommandCursor) -> list:
    plot = []
    for item in data:
        plot.append({"name": item.get("name"), "value": get_works_h_index_by_scholar_citations(item.get("works"))})
    return plot


@get_percentage
def parse_articles_by_publisher(works: Generator) -> list:
    data = map(
        lambda x: (
            x.source.publisher.name
            if x.source.publisher and isinstance(x.source.publisher.name, str)
            else "Sin información"
        ),
        works,
    )
    counter = Counter(data)
    plot = []
    for name, value in counter.items():
        plot += [{"name": name, "value": value}]
    return plot


@get_percentage
def parse_products_by_subject(works: Generator) -> list:
    data = chain.from_iterable(
        map(
            lambda x: [sub for subject in x.subjects for sub in subject.subjects if subject.source == "openalex"],
            works,
        )
    )
    results = Counter(subject.name for subject in data)
    plot = []
    for name, value in results.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def parse_products_by_database(works: Generator) -> list:
    data = chain.from_iterable(map(lambda x: x.updated, works))
    counter = Counter(up.source for up in data)
    plot = []
    for name, value in counter.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def parse_products_by_access_route(works: Generator) -> list:
    data = map(
        lambda x: (
            x.bibliographic_info.open_access_status if x.bibliographic_info.open_access_status else "Sin información"
        ),
        works,
    )
    counter = Counter(data)
    plot = []
    for name, value in counter.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def parse_products_by_author_sex(data: CommandCursor) -> list:
    plot = []
    for item in data:
        if item.get("_id", "") == "":
            plot.append({"name": "Sin información", "value": item.get("works_count", 0)})
            continue
        plot.append({"name": item.get("_id"), "value": item.get("works_count", 0)})
    return plot


@get_percentage
def parse_products_by_age_range(persons: CommandCursor) -> list:
    ranges = {"14-26": (14, 26), "27-59": (27, 59), "60+": (60, float("inf"))}
    result = {"14-26": 0, "27-59": 0, "60+": 0, "Sin información": 0}
    for person in persons:
        if not person.get("birthdate") or person.get("birthdate") == -1:
            result["Sin información"] += person.get("works_count", 0)
            continue
        birthdate = datetime.fromtimestamp(person.get("birthdate")).year
        age = datetime.now().year - birthdate
        for name, (low_age, high_age) in ranges.items():
            if low_age <= age <= high_age:
                result[name] += person.get("works_count", 0)
                break
    plot = []
    for name, value in result.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def parse_articles_by_scienti_category(works: Generator, total_works: int = 0) -> list:
    data = filter(
        lambda x: x.source == "scienti" and x.rank and x.rank.split("_")[-1] in ["A", "A1", "B", "C", "D"],
        chain.from_iterable(map(lambda x: x.ranking, works)),
    )
    counter = Counter(map(lambda x: x.rank.split("_")[-1], data))
    plot = []
    for name, value in counter.items():
        plot.append({"name": name, "value": value})
    plot.append({"name": "Sin información", "value": total_works - sum(counter.values())})
    return plot


@get_percentage
def get_articles_by_scimago_quartile(data: list, total_results: int) -> list:
    plot = [{"name": "Sin información", "value": total_results - len(data)}]
    results = Counter(data)
    for name, value in results.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def get_products_by_same_institution(sources: Iterable, institution: dict) -> list:
    results = {"same": 0, "different": 0, "Sin información": 0}
    names = []
    if institution:
        names = list(set([name["name"].lower() for name in institution["names"]]))
    for source in sources:
        if not source.publisher or not source.publisher.name or not isinstance(source.publisher.name, str):
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

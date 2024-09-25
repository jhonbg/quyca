import json
import os
from math import log

from pandas import read_csv


def parse_coauthorship_by_country_map(data: list) -> dict:
    countries: dict = {}
    for item in data:
        if not "country_code" in item["affiliation"]["addresses"].keys():
            continue
        if item["affiliation"]["addresses"]["country_code"] and item["affiliation"]["addresses"]["country"]:
            country_code = item["affiliation"]["addresses"]["country_code"]
            country_name = item["affiliation"]["addresses"]["country"]
            if country_code in countries.keys():
                countries[country_code]["count"] += item["count"]
            else:
                countries[country_code] = {"count": item["count"], "name": country_name}
    for key, value in countries.items():
        countries[key]["log_count"] = log(value["count"])
    with open(os.path.join(os.path.dirname(__file__), "concerns/worldmap.json"), "r") as worldmap_file:
        plot = json.load(worldmap_file)
    for item, feature in enumerate(plot["features"]):
        if feature["properties"]["country_code"] in countries.keys():
            country_code = feature["properties"]["country_code"]
            plot["features"][item]["properties"]["count"] = countries[country_code]["count"]
            plot["features"][item]["properties"]["log_count"] = countries[country_code]["log_count"]
    return {"plot": plot}


def get_coauthorship_by_colombian_department_map(data: list) -> dict:
    states: dict = {}
    with open(os.path.join(os.path.dirname(__file__), "concerns/cities_by_state.csv"), "r") as cities_by_state_file:
        cities_by_state = read_csv(cities_by_state_file)
    for item in data:
        if not "country_code" in item["affiliation"]["addresses"].keys():
            continue
        if item["affiliation"]["addresses"]["country_code"] and item["affiliation"]["addresses"]["city"]:
            city = item["affiliation"]["addresses"]["city"]
            state = cities_by_state[cities_by_state["MUNICIPIO"] == city]["DEPARTAMENTO"]
            if len(state) == 0:
                continue
            state = state.iloc[0]
            if state in states.keys():
                states[state]["count"] += item["count"]
            else:
                states[state] = {"count": item["count"], "name": state}
    for key, value in states.items():
        states[key]["log_count"] = log(value["count"])
    with open(os.path.join(os.path.dirname(__file__), "concerns/colombiamap.json"), "r") as colombiamap_file:
        plot = json.load(colombiamap_file)
    for item, feature in enumerate(plot["features"]):
        state = (
            feature["properties"]["NOMBRE_DPT"].capitalize()
            if "bogota" not in feature["properties"]["NOMBRE_DPT"].lower()
            else "Bogotá D.C."
        )
        if state in states.keys():
            plot["features"][item]["properties"]["count"] = states[state]["count"]
            plot["features"][item]["properties"]["log_count"] = states[state]["log_count"]
        else:
            plot["features"][item]["properties"]["count"] = 0
            plot["features"][item]["properties"]["log_count"] = 0
    return {"plot": plot}

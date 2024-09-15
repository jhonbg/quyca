import json
import os
from math import log
from typing import Iterable

from pandas import read_csv


def get_coauthorship_by_country_map(works):
    countries = {}
    for work in works:
        if not "country_code" in work["affiliation"]["addresses"].keys():
            continue
        if work["affiliation"]["addresses"]["country_code"] and work["affiliation"]["addresses"]["country"]:
            country_code = work["affiliation"]["addresses"]["country_code"]
            country_name = work["affiliation"]["addresses"]["country"]
            if country_code in countries.keys():
                countries[country_code]["count"] += work["count"]
            else:
                countries[country_code] = {"count": work["count"], "name": country_name}
    for key, val in countries.items():
        countries[key]["log_count"] = log(val["count"])
    with open(os.path.join(os.path.dirname(__file__), "concerns/worldmap.json"), "r") as worldmap_file:
        worldmap = json.load(worldmap_file)
    for item, feat in enumerate(worldmap["features"]):
        if feat["properties"]["country_code"] in countries.keys():
            country_code = feat["properties"]["country_code"]
            worldmap["features"][item]["properties"]["count"] = countries[country_code]["count"]
            worldmap["features"][item]["properties"]["log_count"] = countries[country_code]["log_count"]
    return worldmap


def get_coauthorship_by_colombian_department_map(works: Iterable):
    states = {}
    with open(os.path.join(os.path.dirname(__file__), "concerns/cities_by_state.csv"), "r") as cities_by_state_file:
        cities_by_state = read_csv(cities_by_state_file)
    for work in works:
        if not "country_code" in work["affiliation"]["addresses"].keys():
            continue
        if work["affiliation"]["addresses"]["country_code"] and work["affiliation"]["addresses"]["city"]:
            city = work["affiliation"]["addresses"]["city"]
            state = cities_by_state[cities_by_state["MUNICIPIO"] == city]["DEPARTAMENTO"]
            if len(state) == 0:
                continue
            state = state.iloc[0]
            if state in states.keys():
                states[state]["count"] += work["count"]
            else:
                states[state] = {"count": work["count"], "name": state}
    for key, value in states.items():
        states[key]["log_count"] = log(value["count"])
    with open(os.path.join(os.path.dirname(__file__), "concerns/colombiamap.json"), "r") as colombiamap_file:
        colombiamap = json.load(colombiamap_file)
    for item, feat in enumerate(colombiamap["features"]):
        dep_name = (
            feat["properties"]["NOMBRE_DPT"].capitalize()
            if "bogota" not in feat["properties"]["NOMBRE_DPT"].lower()
            else "Bogotá D.C."
        )
        if dep_name in states.keys():
            colombiamap["features"][item]["properties"]["count"] = states[dep_name]["count"]
            colombiamap["features"][item]["properties"]["log_count"] = states[dep_name]["log_count"]
        else:
            colombiamap["features"][item]["properties"]["count"] = 0
            colombiamap["features"][item]["properties"]["log_count"] = 0
    return colombiamap

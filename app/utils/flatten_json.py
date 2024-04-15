import csv
from typing import Any
import datetime


def flatten_json(
    json_data: dict[str, dict | list | float | str],
    config: dict[str, list[str]],
    level: int = 0,
    separator: str = "/",
    parent_key: str = "",
):
    flat_data = {}
    # remove from json_data

    for key, value in json_data.items():
        if key in config.get("remove", []):
            continue
        new_key = parent_key + separator + key if parent_key else key

        if level > 0 and isinstance(value, dict) and new_key in config.keys():
            flat_data.update(flatten_json(value, config, level - 1, separator, new_key))
        elif (
            level > 0
            and isinstance(value, list)
            and all(isinstance(item, dict) for item in value)
        ):
            list_data = []
            for item in value:
                list_data.append(flatten_json(item, config, level - 1, separator))
            if new_key in config:
                flat_data[config[new_key]["name"]] = (
                    eval(config[new_key]["expresion"])
                    if "expresion" in config[new_key]
                    else " | ".join(
                        map(
                            lambda x: " / ".join(
                                str(x[_key]) for _key in config[new_key]["fields"]
                            ),
                            list_data,
                        )
                    )
                )
        elif new_key in config and isinstance(value, dict):
            attributes = config[new_key]["fields"]
            combined_values = [f"{attr}:{value.get(attr, '')}" for attr in attributes]
            flat_data[config[new_key]["name"]] = " | ".join(combined_values)
        else:
            if not isinstance(value, dict) or not isinstance(value, list):
                key = config.get(new_key)["name"] if new_key in config else new_key
                if new_key in config and "expresion" in config[new_key]:
                    flat_data[key] = eval(config[new_key]["expresion"]) if value else ""
                else:
                    flat_data[key] = str(value)

    return flat_data


def flatten_json_list(
    json_list: list[dict[str, dict | list | str | float]],
    config: dict[str, list[str]],
    level=0,
) -> list[dict[str, Any]]:
    flat_data_list = []

    for json_data in json_list:
        flat_data = flatten_json(json_data, config, level)
        flat_data_list.append(flat_data)

    return flat_data_list

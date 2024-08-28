import csv
from typing import Any
import datetime


def get_flat_data(data: list, config: dict, level=0) -> list:
    flat_data = []
    for item in data:
        flat_item = get_flat_item(item, config, level)
        flat_data.append(flat_item)
    return flat_data


def get_flat_item(
    item: dict, config: dict, level: int = 0, separator: str = "/", parent_key: str = ""
):
    flat_item = {}

    for key in config.keys():
        value = item.get(key, "")
        new_key = parent_key + separator + key if parent_key else key

        if level > 0 and isinstance(value, dict) and new_key in config.keys():
            new_key = config.get(new_key, {"name": new_key})["name"]
            config = config[key].get("config", config)
            flat_item.update(
                get_flat_item(value, config, level - 1, separator, new_key)
            )
        elif (
            level > 0
            and isinstance(value, list)
            and all(isinstance(item, dict) for item in value)
        ):
            list_data = []
            for item in value:
                _config = config[key].get("config", config)
                list_data.append(get_flat_item(item, _config, level - 1, separator))
            if new_key in config:
                flat_item[config[key]["name"]] = (
                    eval(config[key]["expresion"])
                    if "expresion" in config[key]
                    else " | ".join(
                        map(
                            lambda x: " / ".join(
                                str(x[_key]) for _key in config[key]["fields"]
                            ),
                            list_data,
                        )
                    )
                )
        elif new_key in config and isinstance(value, dict):
            attributes = config[key]["fields"]
            combined_values = [f"{attr}:{value.get(attr, '')}" for attr in attributes]
            flat_item[config[key]["name"]] = " | ".join(combined_values)
        else:
            if not isinstance(value, dict) or not isinstance(value, list):
                _key = config[key]["name"] if key in config else new_key
                if key in config and "expresion" in config[key]:
                    flat_item[_key] = eval(config[key]["expresion"]) if value else ""
                else:
                    flat_item[_key] = str(value)

    return flat_item

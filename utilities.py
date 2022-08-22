import json


def load_json_from_pat(filepath: str) -> dict:
    try:
        with open(filepath) as json_file:
            data = json.load(json_file)
    except Exception as ex:
        print(f"Couldn't load json from: {filepath}. Reason: {ex}")
    return data

import json

def get_settings() -> dict[str, str]:
    with open("settings.json", "r") as file:
        return json.load(file)

def get_iteration_name() -> str:
    return get_settings()["iteration name"]

def get_data_file() -> str:
    return get_settings()["data file"]

def get_sheet_id() -> str:
    return get_settings()["sheet id"]
 

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
 
def get_graph_size() -> tuple[float, float]:
        graph_length, graph_height = map(float, get_settings()["graph size"].split("x"))
        return (graph_length, graph_height)

def get_title_font_size() -> float:
        return float(get_settings()["title size"])

def get_axis_font_size() -> float:
        return float(get_settings()["axes size"])

def get_legend_font_size() -> float:
        return float(get_settings()["legend size"])

def get_table_files() -> list[str]:
        return list(get_settings()["table files"])

def get_show_graphs() -> bool:
    return bool(get_settings()["show graphs"])

def get_graphs_save_location() -> str:
    return get_settings()["graphs save location"]


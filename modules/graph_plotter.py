import matplotlib
import matplotlib.pyplot as plt
import json
import tkinter # Necessary for TkAgg

def get_graph_size() -> tuple[float, float]:
    with open("settings.json") as file:
        settings = json.load(file)
        graph_length, graph_height = map(float, settings["graph size"].split("x"))
        return (graph_length, graph_height)

def get_title_font_size() -> float:
    with open("settings.json") as file:
        settings = json.load(file)
        return float(settings["title size"])

def get_axis_font_size() -> float:
    with open("settings.json") as file:
        settings = json.load(file)
        return float(settings["axes size"])

def get_legend_font_size() -> float:
    with open("settings.json") as file:
        settings = json.load(file)
        return float(settings["legend size"])

def plot_graph(x_name: str, y_name: str) -> None:
    axis_font_size = get_axis_font_size()
    plt.xlabel(x_name, fontsize=axis_font_size)
    plt.ylabel(y_name, fontsize=axis_font_size)
    plt.title(f"Gráfico {y_name} x {x_name}", fontsize=get_title_font_size())
    plt.legend(fontsize=get_legend_font_size())
    plt.grid(True)
    matplotlib.use("TkAgg")
    plt.show()


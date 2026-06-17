import modules.settings_getter as settings_getter
import matplotlib
import matplotlib.pyplot as plt
import tkinter # Necessary for TkAgg

def plot_graph(x_name: str, y_name: str) -> None:
    axis_font_size = settings_getter.get_axis_font_size()
    plt.xlabel(x_name, fontsize=axis_font_size)
    plt.ylabel(y_name, fontsize=axis_font_size)
    plt.title(f"Gráfico {y_name} x {x_name}", fontsize=settings_getter.get_title_font_size())
    plt.legend(fontsize=settings_getter.get_legend_font_size())
    plt.grid(True)
    matplotlib.use("TkAgg")
    plt.ylim([0, 0.16])
    if settings_getter.get_graphs_save_location():
        plt.savefig(f"{settings_getter.get_graphs_save_location()}" + f"{y_name} x {x_name}.png".replace("/", "÷"))
    if settings_getter.get_show_graphs():
        plt.show()


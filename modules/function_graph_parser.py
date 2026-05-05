from modules.variable import VariablesList
import modules.option_getter as option_getter
import modules.graph_plotter as graph_plotter
import matplotlib.pyplot as plt
import numpy as np

def parse_function_graph(tokens: list[str], options: dict[str, str], variables: VariablesList) -> None:
    parse_function_graph_recursion(tokens, options, variables, 0)

def parse_function_graph_recursion(tokens: list[str], options: dict[str, str], variables: VariablesList,
                                  iteration: int) -> None:
    if iteration == variables.get_iterations():
        return
    y_name = tokens[0]
    x_name = tokens[1]
    x_linspace = np.linspace(option_getter.get_start(options), option_getter.get_end(options))
    y_linspace = eval(tokens[2], {}, {x_name: x_linspace} | variables.get_dict(iteration))
    plt.figure(figsize=graph_plotter.get_graph_size())
    plt.plot(x_linspace, y_linspace, label=f"Gráfico {y_name} x {x_name}")
    graph_plotter.plot_graph(
                                f"{x_name}({option_getter.get_unit(options, "x")})",
                                f"{y_name}({option_getter.get_unit(options, "y")})"
                            )
    parse_function_graph_recursion(tokens, options, variables, iteration + 1)
    

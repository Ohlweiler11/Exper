from variable import *
from graphplotter import *
import parser
from readvariable import python_float
import numpy as np

def read_function_graph(tokens: list[str], options: dict[str, str], variables: VariablesList) -> None:
    read_function_graph_recursion(tokens, options, variables, 0)

def read_function_graph_recursion(tokens: list[str], options: dict[str, str], variables: VariablesList,
                                  iteration: int) -> None:
    if iteration == variables.get_iterations():
        return
    y_name = tokens[0]
    x_name = tokens[1]
    if "-s" in options.keys():
        start = python_float(options["-s"])
    else:
        start = 0
    if "-e" in options.keys():
        end = python_float(options["-e"])
    else:
        end = 100
    x_linspace = np.linspace(start, end)
    y_linspace = eval(tokens[2], {}, {x_name: x_linspace} | variables.get_dict(iteration))
    plt.figure(figsize=get_graph_size())
    plt.plot(x_linspace, y_linspace, label=f"Gráfico {y_name} x {x_name}")
    plot_graph(
                    f"{x_name}({parser.get_unit(options, "x")})",
                    f"{y_name}({parser.get_unit(options, "y")})"
                )
    read_function_graph_recursion(tokens, options, variables, iteration + 1)
    

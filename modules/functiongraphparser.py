from modules.variable import VariablesList
import modules.optiongetter as optiongetter
import modules.graphplotter as graphplotter
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
    x_linspace = np.linspace(optiongetter.get_start(options), optiongetter.get_end(options))
    y_linspace = eval(tokens[2], {}, {x_name: x_linspace} | variables.get_dict(iteration))
    plt.figure(figsize=graphplotter.get_graph_size())
    plt.plot(x_linspace, y_linspace, label=f"Gráfico {y_name} x {x_name}")
    graphplotter.plot_graph(
                                f"{x_name}({optiongetter.get_unit(options, "x")})",
                                f"{y_name}({optiongetter.get_unit(options, "y")})"
                            )
    parse_function_graph_recursion(tokens, options, variables, iteration + 1)
    

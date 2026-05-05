from variable import *
from graphplotter import *
from readequation import evaluated_values
import parser
from uncertainties import ufloat
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import numpy.typing as npt

def linear_function(x: float | npt.NDArray[np.float64], a: float, b: float) -> float | npt.NDArray[np.float64]:
    return a * x + b

def plot_linear_fit(x_centrals: list[float], y_centrals: list[float], a_central: float, b_central: float):
    x_fit_linspace = np.linspace(min(x_centrals), max(y_centrals), 100)
    y_fit_linspace = linear_function(x_fit_linspace, a_central, b_central)
    plt.plot(x_fit_linspace, y_fit_linspace, 'r--', label=f"Reta de ajuste linear")

def linear_fit(options: dict[str, str], x_centrals: list[float], y_centrals: list[float],
               y_uncertainties: list[float]) -> VariablesList:
    if "-lb" in options.keys():
        fit_function = linear_function
        parameters_names = [options["-la"], options["-lb"]]
        parameters_units = [parser.get_unit(options, "la"), parser.get_unit(options, "la")]
    else:
        fit_function = lambda x, a: linear_function(x, a, 0)
        parameters_names = [options["-la"]]
        parameters_units = [parser.get_unit(options, "la")]
    centrals, uncertainty_matrix = curve_fit(
                                                fit_function,
                                                x_centrals,
                                                y_centrals,
                                                sigma=y_uncertainties,
                                                absolute_sigma=True
                                            )
    uncertainties = np.sqrt(np.diag(uncertainty_matrix))
    if "-lb" in options.keys():
        a_central, b_central = centrals
    else:
        a_central = centrals[0]
        b_central = 0
    plot_linear_fit(x_centrals, y_centrals, a_central, b_central)
    return VariablesList(
                            [
                                Variable(parameters_names[i], parameters_units[i], ufloat(centrals[i], uncertainties[i]))
                                for i in range(len(centrals))
                            ]
                        )

def read_points_graph(tokens: list[str], options: dict[str, str], variables: VariablesList) -> VariablesList:
    y_formula = tokens[0]
    x_formula = tokens[1]
    x_centrals = [value.n for value in evaluated_values(x_formula, variables)]
    y_centrals = [value.n for value in evaluated_values(y_formula, variables)]
    x_uncertainties = [value.std_dev for value in evaluated_values(x_formula, variables)]
    y_uncertainties = [value.std_dev for value in evaluated_values(y_formula, variables)]
    plt.figure(figsize=get_graph_size())
    plt.errorbar(
                    x_centrals, y_centrals, xerr=x_uncertainties, yerr=y_uncertainties,
                    fmt="o", capsize=5, label="Dados experimentais com incerteza"
                 )
    if "-la" in options.keys():
        new_variables = linear_fit(options, x_centrals, y_centrals, y_uncertainties)
    else:
        new_variables = VariablesList()
    plot_graph(
                    f"{x_formula}({parser.get_unit(options, "x")})",
                    f"{y_formula}({parser.get_unit(options, "y")})"
                )
    return new_variables

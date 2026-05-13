from modules.variable import Variable, VariablesList
import modules.option_getter as option_getter
import modules.equation_parser as equation_parser
import modules.fit_functions as fit_functions
import modules.graph_plotter as graph_plotter
import modules.settings_getter as settings_getter
from uncertainties import ufloat
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

def parse_points_graph(tokens: list[str], options: dict[str, str], variables: VariablesList) -> VariablesList:
    y_formula = tokens[0]
    x_formula = tokens[1]
    x_centrals = [value.n for value in equation_parser.evaluated_values(x_formula, variables)]
    y_centrals = [value.n for value in equation_parser.evaluated_values(y_formula, variables)]
    x_uncertainties = [value.std_dev for value in equation_parser.evaluated_values(x_formula, variables)]
    y_uncertainties = [value.std_dev for value in equation_parser.evaluated_values(y_formula, variables)]
    plt.figure(figsize=settings_getter.get_graph_size())
    plt.errorbar(
                    x_centrals, y_centrals, xerr=x_uncertainties, yerr=y_uncertainties,
                    fmt="o", capsize=5, label="Dados experimentais com incerteza"
                 )
    if option_getter.has_b_parameter(options) or option_getter.has_a_parameter(options) in options.keys():
        new_variables = linear_fit(options, x_centrals, y_centrals, y_uncertainties)
    else:
        new_variables = VariablesList()
    graph_plotter.plot_graph(
                                f"{x_formula} ({option_getter.get_unit(options, "x")})",
                                f"{y_formula} ({option_getter.get_unit(options, "y")})"
                            )   
    return new_variables

def plot_linear_fit(x_centrals: list[float], a_central: float, b_central: float):
    x_fit_linspace = np.linspace(min(x_centrals), max(x_centrals), 100)
    y_fit_linspace = fit_functions.linear_function(x_fit_linspace, a_central, b_central)
    plt.plot(x_fit_linspace, y_fit_linspace, 'r--', label=f"Reta de ajuste linear")

def linear_fit(options: dict[str, str], x_centrals: list[float], y_centrals: list[float],
               y_uncertainties: list[float]) -> VariablesList:
    parameters_names = option_getter.get_linear_parameters_names(options)
    parameters_units = option_getter.get_linear_parameters_units(options)
    centrals, uncertainty_matrix = curve_fit(
                                                option_getter.get_fit_function(options),
                                                x_centrals,
                                                y_centrals,
                                                sigma=y_uncertainties,
                                                absolute_sigma=True
                                            )
    uncertainties = np.sqrt(np.diag(uncertainty_matrix))
    if option_getter.has_a_parameter(options) and option_getter.has_b_parameter(options):
        a_central, b_central = centrals
    elif option_getter.has_a_parameter(options):
        a_central = centrals[0]
        b_central = 0
    else:
        a_central = 0
        b_central = centrals[0]
    plot_linear_fit(x_centrals, a_central, b_central)
    return VariablesList(
                            [
                                Variable(parameters_names[i], parameters_units[i], ufloat(centrals[i], uncertainties[i]))
                                for i in range(len(centrals))
                            ]
                        )


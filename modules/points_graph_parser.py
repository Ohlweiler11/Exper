from modules.variable import Variable, VariablesList
import modules.option_getter as option_getter
import modules.equation_parser as equation_parser
import modules.fit_functions as fit_functions
import modules.graph_plotter as graph_plotter
import modules.settings_getter as settings_getter
from uncertainties import ufloat
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt

def parse_points_graph(tokens: list[str], options: dict[str, str], variables: VariablesList) -> VariablesList:
    y_formula = tokens[0]
    x_formula = tokens[1]
    x_centrals = np.array([value.n for value in equation_parser.evaluated_values(x_formula, variables)])
    y_centrals = np.array([value.n for value in equation_parser.evaluated_values(y_formula, variables)])
    x_uncertainties = np.array([value.std_dev for value in equation_parser.evaluated_values(x_formula, variables)])
    y_uncertainties = np.array([value.std_dev for value in equation_parser.evaluated_values(y_formula, variables)])
    plt.figure(figsize=settings_getter.get_graph_size())
    plt.errorbar(
                    x_centrals, y_centrals, xerr=x_uncertainties, yerr=y_uncertainties,
                    fmt="o", capsize=5, label="Dados experimentais com incerteza"
                 )
    if option_getter.has_a_parameter(options) or option_getter.has_b_parameter(options):
        new_variables = linear_fit(options, x_centrals, y_centrals, y_uncertainties)
    else:
        new_variables = VariablesList()
    graph_plotter.plot_graph(
                                f"{x_formula} ({option_getter.get_unit(options, "x")})",
                                f"{y_formula} ({option_getter.get_unit(options, "y")})"
                            )   
    return new_variables

def plot_linear_fit(x_centrals: npt.NDArray, a_central: float, b_central: float) -> None:
    x_fit_linspace = np.linspace(min(x_centrals), max(x_centrals), 100)
    y_fit_linspace = fit_functions.linear_function(x_fit_linspace, a_central, b_central)
    plt.plot(x_fit_linspace, y_fit_linspace, 'r--', label=f"Reta de ajuste linear")

def linear_fit(options: dict[str, str], x_centrals: npt.NDArray, y_centrals: npt.NDArray,
               y_uncertainties: npt.NDArray) -> VariablesList:
    weights = 1 / y_uncertainties
    if option_getter.has_a_parameter(options) and option_getter.has_b_parameter(options):
        centrals, uncertainties = np.polyfit(x_centrals, y_centrals, deg=1, w=weights, cov=True)
        a_central, b_central = centrals
        a_uncertainty, b_uncertainty = uncertainties
        plot_linear_fit(x_centrals, a_central, b_central)
        return VariablesList(
                                [
                                    Variable(
                                                option_getter.get_a_parameter_name(options),
                                                option_getter.get_a_parameter_unit(options),
                                                ufloat(a_central, a_uncertainty)
                                            ),
                                    Variable(
                                                option_getter.get_b_parameter_name(options),
                                                option_getter.get_b_parameter_unit(options),
                                                ufloat(b_central, b_uncertainty)
                                            )
                                ]
                            )
    elif option_getter.has_a_parameter(options):
        a_central = np.sum(weights * x_centrals * y_centrals) / np.sum(weights * x_centrals**2)
        a_uncertainty = np.sqrt(1 / np.sum(weights * x_centrals**2))
        plot_linear_fit(x_centrals, a_central, 0)
        return VariablesList(
                                Variable(
                                            option_getter.get_a_parameter_name(options),
                                            option_getter.get_a_parameter_unit(options),
                                            ufloat(a_central, a_uncertainty)
                                        )
                            )
    else:
        b_central = np.sum(weights * y_centrals) / np.sum(weights)
        b_uncertainty = np.sqrt(1 / np.sum(weights))
        plot_linear_fit(x_centrals, 0, b_central)
        return VariablesList(
                                Variable(
                                            option_getter.get_b_parameter_name(options),
                                            option_getter.get_b_parameter_unit(options),
                                            ufloat(b_central, b_uncertainty)
                                        )
                            )


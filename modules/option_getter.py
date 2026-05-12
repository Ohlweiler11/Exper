import modules.formatter as formatter
import modules.fit_functions as fit_functions
from uncertainties.umath import sqrt
from typing import Callable
import numpy as np
import numpy.typing as npt

def get_unit(options: dict[str, str], variable_name: str | None =None) -> str:
    if variable_name == None:
        unit_option = "--u"
    else:
        unit_option = "--u" + variable_name 
    if unit_option in options.keys():
        return options[unit_option]
    else:
        return "adim."

def get_factor(options: dict[str, str]) -> float:
    if "--*" in options.keys():
        return formatter.python_float(options["--*"])
    else:
        return 1

def analog_uncertainty(interval: float) -> float:
    return interval / (2 * sqrt(6))

def digital_uncertainty(interval: float) -> float:
    return interval / (2 * sqrt(3))

def get_general_uncertainty(options: dict[str, str]) -> float:
    if "--g" in options.keys():
        return formatter.python_float(options["--g"])
    else:
        return 0

def get_analog_uncertainty(options: dict[str, str]) -> float:
    if "--a" in options.keys():
        return analog_uncertainty(formatter.python_float(options["--a"]))
    else:
        return 0

def get_digital_uncertainty(options: dict[str, str]) -> float:
    if "--d" in options.keys():
        return analog_uncertainty(formatter.python_float(options["--d"]))
    else:
        return 0

def get_percentage_uncertainty(options: dict[str, str], central: float) -> float:
    if "--%" in options.keys():
        return (formatter.python_float(options["--%"]) * central) / 100
    else:
        return 0

def has_a_parameter(options: dict[str, str]) -> bool:
    return "--la" in options.keys()

def has_b_parameter(options: dict[str, str]) -> bool:
    return "--lb" in options.keys()

def get_linear_parameters_names(options: dict[str, str]) -> list[str]:
    if has_a_parameter(options) and has_b_parameter(options):
        return [options["--la"], options["--lb"]]
    elif has_a_parameter(options):
        return [options["--la"]]
    else:
        return [options["--lb"]]

def get_linear_parameters_units(options: dict[str, str]) -> list[str]:
    if has_a_parameter(options) and has_b_parameter(options):
        return [get_unit(options, "la"), get_unit(options, "lb")]
    elif has_a_parameter(options):
        return [get_unit(options, "la")]
    else:
        return [get_unit(options, "lb")]

def get_fit_function(options: dict[str, str]) -> Callable[
                     [float | npt.NDArray[np.float64], float, float], float | npt.NDArray[np.float64]] | Callable[
                     [float | npt.NDArray[np.float64], float], float | npt.NDArray[np.float64]]:

    if has_a_parameter(options) and has_b_parameter(options):
        return fit_functions.linear_function
    elif has_a_parameter(options):
        return lambda x, a: fit_functions.linear_function(x, a, 0)
    else:
        return lambda x, b: fit_functions.linear_function(x, 0, b)


def get_start(options: dict[str, str]) -> float:
    if "--s" in options.keys():
        return formatter.python_float(options["--s"])
    else:
        return 0

def get_end(options: dict[str, str]) -> float:
    if "--e" in options.keys():
        return formatter.python_float(options["--e"])
    else:
        return 100

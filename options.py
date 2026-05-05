import parser
from uncertainties.umath import sqrt
from readpointsgraph import linear_function
from typing import Callable
import numpy as np
import numpy.typing as npt

def get_unit(options: dict[str, str], variable_name: str | None =None) -> str:
    if variable_name == None:
        unit_option = "-u"
    else:
        unit_option = "-u" + variable_name 
    if unit_option in options.keys():
        return options[unit_option]
    else:
        return "adimensional"

def get_factor(options: dict[str, str]) -> float:
    if "-*" in options.keys():
        return parser.python_float(options["-*"])
    else:
        return 1

def analog_uncertainty(interval: float) -> float:
    return interval / (2 * sqrt(6))

def digital_uncertainty(interval: float) -> float:
    return interval / (2 * sqrt(3))

def get_analog_uncertainty(options: dict[str, str]) -> float:
    if "-a" in options.keys():
        return analog_uncertainty(parser.python_float(options["-a"]))
    else:
        return 0

def get_digital_uncertainty(options: dict[str, str]) -> float:
    if "-d" in options.keys():
        return analog_uncertainty(parser.python_float(options["-d"]))
    else:
        return 0

def get_percentage_uncertainty(options: dict[str, str], central: float) -> float:
    if "-%" in options.keys():
        return (parser.python_float(options["-%"]) * central) / 100
    else:
        return 0

def has_b_parameter(options: dict[str, str]) -> bool:
    return "-lb" in options.keys()

def get_linear_parameters_names(options: dict[str, str]) -> list[str]:
    if has_b_parameter(options):
        return [options["-la"], options["-lb"]]
    else:
        return [options["-la"]]

def get_linear_parameters_units(options: dict[str, str]) -> list[str]:
    if has_b_parameter(options):
        return [get_unit(options, "la"), get_unit(options, "lb")]
    else:
        return [get_unit(options, "la")]

def get_fit_function(options: dict[str, str]) -> Callable[
                     [float | npt.NDArray[np.float64], float, float], float | npt.NDArray[np.float64]] | Callable[
                     [float | npt.NDArray[np.float64], float], float | npt.NDArray[np.float64]]:
    if has_b_parameter(options):
        return linear_function
    else:
        return (lambda x, a: linear_function(x, a, 0))


def get_start(options: dict[str, str]) -> float:
    if "-s" in options.keys():
        return parser.python_float(options["-s"])
    else:
        return 0

def get_end(options: dict[str, str]) -> float:
    if "-e" in options.keys():
        return parser.python_float(options["-e"])
    else:
        return 100

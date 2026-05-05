import parser
from variable import *
from uncertainties import UFloat, ufloat
from uncertainties.umath import sqrt

def analog_uncertainty(interval: float) -> float:
    return interval / (2 * sqrt(6))

def digital_uncertainty(interval: float) -> float:
    return interval / (2 * sqrt(3))

def python_float(value: str) -> float:
    return float(value.replace(",", "."))

def combined_uncertainty(uncertainties: list[float]) -> float:
    return sqrt(sum([uncertainty * uncertainty for uncertainty in uncertainties]))

def option_uncertainty(central: float, option: str, value: float) -> float:
    match option:
        case "-a":
            return analog_uncertainty(value)
        case "-d":
            return digital_uncertainty(value)
        case "-%":
            return (central * value) / 100
        case _:
            raise SyntaxError(f"no {option} option")

def get_uncertainty(central: float, base_uncertainty: float, uncertainty_options: dict[str, float]) -> float:
    return combined_uncertainty(
                                    [base_uncertainty] +
                                    [
                                        option_uncertainty(central, option, uncertainty_options[option])
                                        for option in uncertainty_options.keys()
                                    ]
                                )

def variable_ufloat(value: str, factor: float, uncertainty_options: dict[str, float]) -> UFloat:
    if "~" in value:
        base_central = python_float(value.split("~")[0])
        base_uncertainty = python_float(value.split("~")[1])
    else:
        base_central = python_float(value)
        base_uncertainty = 0
    central = base_central * factor
    uncertainty = get_uncertainty(central, base_uncertainty, uncertainty_options)
    return ufloat(central, uncertainty)

def read_variable(tokens: list[str], options: dict[str, str]) -> Variable:
    if "-*" in options.keys():
        factor = python_float(options["-*"])
    else:
        factor = 1
    uncertainty_options = {
                                option: python_float(options[option])
                                for option in options.keys() if options != "-u" and options != "-*"
                            }
    return Variable(
                        tokens[0], parser.get_unit(options),
                        [
                            variable_ufloat(value, factor, uncertainty_options)
                            for value in tokens[1:] if value[0] != "-"
                        ]
                    )


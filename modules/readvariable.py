import modules.parser as parser
from modules.variable import *
from modules.options import get_unit, get_factor, get_analog_uncertainty, get_digital_uncertainty, get_percentage_uncertainty
from uncertainties import UFloat, ufloat
from uncertainties.umath import sqrt

def get_uncertainty(central: float, base_uncertainty: float, options: dict[str, str]) -> float:
    return sqrt(
                    base_uncertainty**2 +
                    get_analog_uncertainty(options)**2 +
                    get_digital_uncertainty(options)**2 +
                    get_percentage_uncertainty(options, central)**2
                )

def variable_ufloat(value: str, factor: float, options: dict[str, str]) -> UFloat:
    if "~" in value:
        base_central = parser.python_float(value.split("~")[0])
        base_uncertainty = parser.python_float(value.split("~")[1])
    else:
        base_central = parser.python_float(value)
        base_uncertainty = 0 
    central = base_central * factor
    uncertainty = get_uncertainty(central, base_uncertainty, options)
    return ufloat(central, uncertainty)

def read_variable(tokens: list[str], options: dict[str, str]) -> Variable:
    return Variable(
                        tokens[0], get_unit(options),
                        [
                            variable_ufloat(value, get_factor(options), options)
                            for value in tokens[1:] if value[0] != "-"
                        ]
                    )


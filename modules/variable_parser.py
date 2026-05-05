from modules.variable import Variable
import modules.formatter as formatter
import modules.option_getter as option_getter
from uncertainties import UFloat, ufloat
from uncertainties.umath import sqrt

def get_uncertainty(central: float, base_uncertainty: float, options: dict[str, str]) -> float:
    return sqrt(
                    base_uncertainty**2 +
                    option_getter.get_analog_uncertainty(options)**2 +
                    option_getter.get_digital_uncertainty(options)**2 +
                    option_getter.get_percentage_uncertainty(options, central)**2
                )

def variable_ufloat(value: str, factor: float, options: dict[str, str]) -> UFloat:
    if "~" in value:
        base_central = formatter.python_float(value.split("~")[0])
        base_uncertainty = formatter.python_float(value.split("~")[1])
    else:
        base_central = formatter.python_float(value)
        base_uncertainty = 0 
    central = base_central * factor
    uncertainty = get_uncertainty(central, base_uncertainty, options)
    return ufloat(central, uncertainty)

def parse_variable(tokens: list[str], options: dict[str, str]) -> Variable:
    return Variable(
                        tokens[0], option_getter.get_unit(options),
                        [
                            variable_ufloat(value, option_getter.get_factor(options), options)
                            for value in tokens[1:] if value[0] != "-"
                        ]
                    )


import modules.formatter as formatter
from uncertainties.umath import sqrt

def get_unit(options: dict[str, str], variable_name: str | None = None) -> str:
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

def get_a_parameter_name(options: dict[str, str]) -> str:
    return options["--la"]

def get_b_parameter_name(options: dict[str, str]) -> str:
    return options["--lb"]

def get_a_parameter_unit(options: dict[str, str]) -> str:
    return options["--ula"]

def get_b_parameter_unit(options: dict[str, str]) -> str:
    return options["--ulb"]

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

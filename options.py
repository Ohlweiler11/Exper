from readvariable import python_float

def get_unit(options: dict[str, str], specification: str | None =None) -> str:
    if specification == None:
        unit_option = "-u"
    else:
        unit_option = "-u" + specification
    if unit_option in options.keys():
        return options[unit_option]
    else:
        return "adimensional"


def get_factor(options: dict[str, str]) -> float:
    if "-*" in options.keys():
        return python_float(options["-*"])
    else:
        return 1

def get_start(options: dict[str, str]) -> float:
    if "-s" in options.keys():
        return python_float(options["-s"])
    else:
        return 0

def get_end(options: dict[str, str]) -> float:
    if "-e" in options.keys():
        return python_float(options["-e"])
    else:
        return 100

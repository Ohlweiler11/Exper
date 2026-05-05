def parse_tokens(line: str) -> list[str]:
    parts = line.split()
    return [parts[i] for i in range(len(parts)) if parts[i] != "-" and parts[i - 1] != "-"]

def parse_options(line: str) -> dict[str, str]:
    parts = line.split()
    return {parts[i]: parts[i + 1] for i in range(len(parts)) if parts[i][0] == "-"}

def get_unit(options: dict[str, str], specification: str | None =None) -> str:
    if specification == None:
        unit_option = "-u"
    else:
        unit_option = "-u" + specification
    if unit_option in options.keys():
        return options[unit_option]
    else:
        return "adimensional"


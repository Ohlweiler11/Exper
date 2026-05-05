def parse_tokens(line: str) -> list[str]:
    parts = line.split()
    return [parts[i] for i in range(len(parts)) if parts[i] != "-" and parts[i - 1] != "-"]

def parse_options(line: str) -> dict[str, str]:
    parts = line.split()
    return {parts[i]: parts[i + 1] for i in range(len(parts)) if parts[i][0] == "-"}

def python_float(value: str) -> float:
    return float(value.replace(",", "."))


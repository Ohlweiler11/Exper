def get_main_tokens(line: str) -> list[str]:
    tokens = line.split()
    return [tokens[i] for i in range(len(tokens)) if tokens[i][:2] != "--" and tokens[i - 1][:2] != "--"]

def get_options(line: str) -> dict[str, str]:
    tokens = line.split()
    return {tokens[i]: tokens[i + 1] for i in range(len(tokens)) if tokens[i][:2] == "--"}



def get_main_tokens(line: str) -> list[str]:
    tokens = line.split()
    return [tokens[i] for i in range(len(tokens)) if tokens[i][:2]]

def get_options(line: str) -> dict[str, str]:
    tokens = line.split()
    return {token.split("=")[0]: token.split("=")[1] for token in tokens if token[:2] == "--"}



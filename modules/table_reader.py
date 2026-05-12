from modules.variable import Variable, VariablesList
import modules.tokenizer as tokenizer
import modules.variable_parser as variable_parser
import json

def read_tables(table_files: list[str]) -> VariablesList:
    if len(table_files) == 0:
        return VariablesList()
    variable_1, variable_2 = read_table(table_files[-1])
    return read_tables(table_files[:-1]) + variable_1 + variable_2


def read_table(table_file: str) -> tuple[Variable, Variable]:
    table = table_lines(table_file)
    line_variable_1 = no_var_line(table[0]) + " ".join([line.split()[0] for line in table[2:]])
    line_variable_2 = no_var_line(table[1]) + " ".join([line.split()[1] for line in table[2:]])
    return (
                variable_parser.parse_variable(
                                                    tokenizer.get_main_tokens(line_variable_1),
                                                    tokenizer.get_options(line_variable_1)
                                                ), 
                variable_parser.parse_variable(
                                                    tokenizer.get_main_tokens(line_variable_2),
                                                    tokenizer.get_options(line_variable_2)
                                                )
            )

def no_var_line(line: str) -> str:
    if line.split()[0] == "var":
        return line[4:]
    return line

def table_lines(table_file) -> list[str]:
    with open(table_file) as file:
        return list(file)

def table_file() -> list[str]:
    with open("settings.json") as file:
        settings = json.load(file)
        return settings["table files"]

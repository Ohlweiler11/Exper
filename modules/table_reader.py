from modules.variable import VariablesList
import modules.tokenizer as tokenizer
import modules.variable_parser as variable_parser
import json

def table_file_specified() -> bool:
    with open("settings.json") as file:
        settings = json.load(file)
        return "table file" in settings.keys()

def read_table() -> VariablesList:
    table = table_lines()
    line_variable_1 = no_var_line(table[0]) + " ".join([line.split()[0] for line in table[2:]])
    line_variable_2 = no_var_line(table[1]) + " ".join([line.split()[1] for line in table[2:]])
    return VariablesList(
                            [
                                variable_parser.parse_variable(
                                                                    tokenizer.get_main_tokens(line_variable_1),
                                                                    tokenizer.get_options(line_variable_1)
                                                                ), 
                                variable_parser.parse_variable(
                                                                    tokenizer.get_main_tokens(line_variable_2),
                                                                    tokenizer.get_options(line_variable_2)
                                                                )
                            ]
                        )

def no_var_line(line: str) -> str:
    if line.split()[0] == "var":
        return line[4:]
    return line

def table_lines() -> list[str]:
    with open(table_file()) as file:
        return list(file)

def table_file() -> str:
    with open("settings.json") as file:
        settings = json.load(file)
        return settings["table file"]

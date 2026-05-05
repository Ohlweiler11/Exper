from modules.variable import *
import modules.parser as parser
from modules.readvariable import read_variable
from modules.readequation import read_equation
from modules.readpointsgraph import read_points_graph
from modules.readfunctiongraph import read_function_graph
import json

def read_commands(lines: list[str]) -> VariablesList:
    if len(lines) == 0:
        return VariablesList()
    variables = read_commands(lines[:-1])
    tokens = parser.parse_tokens(lines[-1])
    options = parser.parse_options(lines[-1])
    if tokens == [] or tokens[0] == "#":
        return variables
    try:
        if (len(lines) == 0):
            return variables
        if tokens[0] == "var":
            return read_variable(tokens[1:], options) + variables
        if tokens[0] == "eqn":
            return read_equation(tokens[1:], options, variables) + variables
        if tokens[0] == "ptg":
            return read_points_graph(tokens[1:], options, variables) + variables
        if tokens[0] == "fng":
            read_function_graph(tokens[1:], options, variables)
            return variables
        raise SyntaxError("invalid section")
    except Exception as exception:
        line_number = len(lines)
        print(f"Line {line_number}:")
        raise exception

def read_lines(data_file: str) -> list[str]:
    with open (data_file) as file:
        return [lines for lines in file] 

def print_results_recursion(variable: Variable, iteration: int) -> None:
    if iteration == variable.get_iterations():
        return
    print(f"{iteration + 1} : {variable.formated_value(iteration)}")
    print_results_recursion(variable, iteration + 1)


def print_results(variables: VariablesList, iteration_name: str) -> None:
    for variable in variables.variables:
        if variable.get_iterations() == 1:
            print(f"{variable.name_and_unit()} : {variable.formated_value(0)}")
        else:
            print(f"{iteration_name} : {variable.name_and_unit()}")
            print_results_recursion(variable, 0)

def main() -> None:
    with open("settings.json", "r") as file:
        settings = json.load(file)
    iteration_name = settings["iteration name"]
    variables = read_commands(read_lines(settings["data file"]))
    print_results(variables, iteration_name)
    try:
        import modules.sheetswriter as sheetswriter
        sheetswriter.write_results(variables)
    except:
        print("sheetswriter.py module not used\n")

if __name__ == "__main__":
    main()    

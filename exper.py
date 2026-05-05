from variable import *
import parser
from readvariable import read_variable
from readequation import read_equation
from readpointsgraph import read_points_graph
from readfunctiongraph import read_function_graph
import matplotlib
import tkinter as tk
matplotlib.use("TkAgg")
import json

def read_commands(lines: list[str], variables: VariablesList, line_number: int) -> VariablesList:
    tokens = parser.parse_tokens(lines[0])
    options = parser.parse_options(lines[0])
    if tokens == [] or tokens[0] == "#":
        return read_commands(lines[1:], variables, line_number + 1)
    try:
        if (len(lines) == 0):
            return variables
        if tokens[0] == "var":
            new_variable = read_variable(tokens[1:], options)
            return read_commands(lines[1:], new_variable + variables, line_number + 1)
        if tokens[0] == "eqn":
            new_variable = read_equation(tokens[1:], options, variables)
            return read_commands(lines[1:], new_variable + variables, line_number + 1)
        if tokens[0] == "ptg":
            new_variable = read_points_graph(tokens[1:], options, variables)
            return read_commands(lines[1:], new_variable + variables, line_number + 1)
        if tokens[0] == "fng":
            read_function_graph(tokens[1:], options, variables)
            return read_commands(lines[1:], variables, line_number + 1)
        raise SyntaxError("invalid section")
    except Exception as exception:
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


def print_results(variables: VariablesList, iteration_name: str):
    for variable in variables.variables:
        if variable.is_single_value:
            print(f"{variable.name_and_unit()} : {variable.formated_value(0)}")
        else:
            print(f"{iteration_name} : {variable.name_and_unit()}")
            print_results_recursion(variable, 0)

def main() -> None:
    with open("settings.json", "r") as file:
        settings = json.load(file)
    iteration_name = settings["iteration name"]
    lines = read_lines(settings["data file"])
    variables = read_commands(lines, VariablesList(), 1)
    print_results(variables, iteration_name)
    try:
        import sheetswriter
        sheetswriter.write_results(variables)
    except:
        print("sheetswriter.py module not used\n")

if __name__ == "__main__":
    main()    

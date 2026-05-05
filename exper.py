from modules.variable import Variable, VariablesList
import modules.tokenizer as tokenizer 
import modules.variableparser as variableparser
import modules.equationparser as equationparser 
import modules.pointsgraphparser as pointsgraphparser
import modules.functiongraphparser as functiongraphparser
import json

def parse_lines(lines: list[str]) -> VariablesList:
    if len(lines) == 0:
        return VariablesList()
    variables = parse_lines(lines[:-1])
    main_tokens = tokenizer.get_main_tokens(lines[-1])
    options = tokenizer.get_options(lines[-1])
    if main_tokens == [] or main_tokens[0] == "#":
        return variables
    try:
        if (len(lines) == 0):
            return variables
        if main_tokens[0] == "var":
            return variableparser.parse_variable(main_tokens[1:], options) + variables
        if main_tokens[0] == "eqn":
            return equationparser.parse_equation(main_tokens[1:], options, variables) + variables
        if main_tokens[0] == "ptg":
            return pointsgraphparser.parse_points_graph(main_tokens[1:], options, variables) + variables
        if main_tokens[0] == "fng":
            functiongraphparser.parse_function_graph(main_tokens[1:], options, variables)
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
    variables = parse_lines(read_lines(settings["data file"]))
    print_results(variables, iteration_name)
    try:
        import modules.sheetswriter as sheetswriter
        sheetswriter.write_results(variables)
    except:
        print("sheetswriter.py module not used\n")

if __name__ == "__main__":
    main()    

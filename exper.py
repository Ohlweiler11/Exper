from modules.variable import Variable, VariablesList
import modules.tokenizer as tokenizer 
import modules.variable_parser as variable_parser
import modules.equation_parser as equation_parser 
import modules.points_graph_parser as points_graph_parser
import modules.function_graph_parser as function_graph_parser
import modules.table_reader as table_reader
import modules.settings_getter as settings_getter

def main() -> None:
    iteration_name = settings_getter.get_iteration_name()
    variables = parse_lines(read_lines(settings_getter.get_data_file()))
    print_results(variables, iteration_name)
    try:
        import modules.sheets_writer as sheets_writer
        sheets_writer.write_results(variables)
    except Exception as exception:
        print(f"sheetswriter.py module not used ({exception})\n")

def read_lines(data_file: str) -> list[str]:
    with open (data_file) as file:
        return [lines for lines in file] 

def parse_lines(lines: list[str]) -> VariablesList:
    if len(lines) == 0:
        return table_reader.read_tables()
    variables = parse_lines(lines[:-1])
    main_tokens = tokenizer.get_main_tokens(lines[-1])
    options = tokenizer.get_options(lines[-1])
    try:
        if main_tokens == [] or lines[-1][0] == "#":
            return variables
        if (len(lines) == 0):
            return variables
        if main_tokens[0] == "var":
            return variables + variable_parser.parse_variable(main_tokens[1:], options)
        if main_tokens[0] == "eqn":
            return variables + equation_parser.parse_equation(main_tokens[1:], options, variables)
        if main_tokens[0] == "ptg":
            return variables + points_graph_parser.parse_points_graph(main_tokens[1:], options, variables)
        if main_tokens[0] == "fng":
            function_graph_parser.parse_function_graph(main_tokens[1:], options, variables)
            return variables
        raise SyntaxError("invalid section")
    except Exception as exception:
        print(f"\nLine {len(lines)}:")
        raise exception

def print_results(variables: VariablesList, iteration_name: str) -> None:
    formatted_variables = [
                            [
                                (variable.get_name_and_unit(), variable.formatted_value(0))
                            ]
                            if variable.get_iterations() == 1
                            else 
                            [(place_in_spaces(iteration_name), variable.get_name_and_unit())] + 
                            [
                                (f"{iteration + 1}", variable.formatted_value(iteration))
                                for iteration in range(variable.get_iterations())
                            ]
                            for variable in variables.variables
                        ]
    SEPARATION_SIZE = 50
    print()
    print("-" * SEPARATION_SIZE)
    for formatted_variable in formatted_variables:
        for cells in formatted_variable:
            print(f"{place_in_spaces(cells[0])} : {cells[1]}")
        print("-" * SEPARATION_SIZE)
    print()

def print_results_recursion(variable: Variable, iteration: int) -> None:
    if iteration == variable.get_iterations():
        return
    print_results_recursion(variable, iteration + 1)

def place_in_spaces(string: str) -> str:
    SPACES = 9
    return string + " " * (SPACES - len(string))

if __name__ == "__main__":
    main()

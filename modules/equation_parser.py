from modules.variable import Variable, VariablesList
import modules.option_getter as option_getter
from uncertainties import UFloat

def evaluated_values(formula: str, variables: VariablesList) -> list[UFloat]:
    return [eval(formula, {}, variables.get_dict(iteration)) for iteration in range(variables.get_iterations())]

def parse_equation(tokens: list[str], options: dict[str, str], variables: VariablesList) -> Variable:
    return Variable(tokens[0], option_getter.get_unit(options), evaluated_values(tokens[1], variables))


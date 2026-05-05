from variable import *
from options import get_unit

def evaluated_values(formula: str, variables: VariablesList) -> list[UFloat]:
    return [eval(formula, {}, variables.get_dict(iteration)) for iteration in range(variables.get_iterations())]

def read_equation(tokens: list[str], options: dict[str, str], variables: VariablesList) -> Variable:
    return Variable(tokens[0], get_unit(options), evaluated_values(tokens[1], variables))


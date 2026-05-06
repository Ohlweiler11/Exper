from modules.variable import Variable, VariablesList
import modules.option_getter as option_getter
from uncertainties import UFloat
import ast

def parse_equation(tokens: list[str], options: dict[str, str], variables: VariablesList) -> Variable:
    return Variable(tokens[0], option_getter.get_unit(options), evaluated_values(tokens[1], variables))

def evaluated_values(formula: str, variables: VariablesList) -> list[UFloat]:
    expression = ast.parse(formula, mode="eval")
    return [
                eval(compile(expression, filename="<ast>", mode="eval"), {}, variables.get_dict(iteration))
                for iteration in range(variables.iterations_of_expression(expression))
            ]




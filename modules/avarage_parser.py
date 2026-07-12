from modules.variable import *
import modules.option_getter as option_getter
import numpy as np

def parse_avarage(tokens: list[str], options: dict[str, str], variables: VariablesList) -> Variable:
    return Variable(
                        tokens[0], option_getter.get_unit(options),
                        np.sum(np.array(variables.get_variable(tokens[1]).values))
                        / len(variables.get_variable(tokens[1]).values)
                    )

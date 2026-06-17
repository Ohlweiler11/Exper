from variable import *
import option_getter
from uncertainties import unumpy as unp
import numpy as np

def parse_avarage(tokens: list[str], options: dict[str, str], variables: VariablesList) -> Variable:
    return Variable(
                        tokens[0], option_getter.get_unit(options),
                        np.sum(unp.uarray(variables.get_variable(tokens[1]).values)) / len(variables.get_variable(tokens[1]).values)
                    )

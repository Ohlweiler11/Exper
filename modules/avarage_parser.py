from modules.variable import Variable, VariablesList
import modules.option_getter as option_getter
from uncertainties import UFloat, ufloat

def parse_avarage(tokens: list[str], options: dict[str ,str], variables: VariablesList) -> VariablesList:
    y = [variable for variable in variables.variables if variable.name == tokens[1]][0]
    x = [variable for variable in variables.variables if variable.name == tokens[2]][0]
    return VariablesList(Variable(tokens[0], option_getter.get_unit(options), avarage_y(x, y)))
        

def avarage_y(x: Variable, y: Variable) -> UFloat:
    area_under_y = sum(
                            [
                                trapezoid_area(y.get_value(i), y.get_value(i + 1), x.get_value(i + 1) - x.get_value(i))
                                for i in range(x.get_iterations() - 1)
                            ],
                            start=ufloat(0, 0)
                        )
    return area_under_y / (y.get_value(-1) - y.get_value(0))
    
def trapezoid_area(base_1: UFloat, base_2: UFloat, height: UFloat) -> UFloat:
    return ((base_1 + base_2) * height) / 2

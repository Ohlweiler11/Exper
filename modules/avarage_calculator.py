from modules.variable import Variable
from uncertainties import UFloat, ufloat

def avarage_y(x: Variable, y: Variable) -> Variable:
    area_under_y = sum(
                            [
                                trapezoid_area(
                                                    y.get_value(i),
                                                    y.get_value(i + 1),
                                                    x.get_value(i + 1) - x.get_value(i)
                                                ),
                                for i in range(x.get_iterations() - 1)
                            ],
                            start=ufloat(0, 0)
                        )
    return area_under_y / y.get_value(-1) - y.get_value(0)
    
def trapezoid_area(base_1: UFloat, base_2: UFloat, height: UFloat) -> UFloat:
    return ((base_1 + base_2) * height) / 2

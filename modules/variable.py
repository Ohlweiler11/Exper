from __future__ import annotations
from uncertainties import UFloat

class Variable:

    def __init__(self, name: str, unit: str, values: list[UFloat] | UFloat):
        self.name = name
        self.unit = unit
        if isinstance(values, list):
            self.values = values
        else:
            self.values = [values]

    def __str__(self):
        return self.name + self.unit + " : " + str(self.values)

    def get_value(self, index: int) -> UFloat:
        if self.get_iterations() == 1:
            return self.values[0]
        else:
            return self.values[index]

    def get_iterations(self) -> int:
        return len(self.values)

    def name_and_unit(self) -> str:
        return self.name + "(" + self.unit + ")"

    def formated_value(self, index):
        value = self.values[index]
        if value.std_dev == float("inf"):
            return f"{str(value.n).replace(".", ",")} ± 0"
        uncertainty_str = str(value.std_dev)
        point_index = uncertainty_str.index(".")
        significant_algarism_index = [i for i, character in enumerate(uncertainty_str) if character not in ".0"][0]
        decimal_places = significant_algarism_index - point_index
        central = str(round(value.n, decimal_places)).replace(".", ",")
        uncertainty = str(round(value.std_dev, decimal_places)).replace(".", ",")
        return f"{central} ± {uncertainty}"

class VariablesList:

    def __init__(self, variables: list[Variable] | Variable | None =None):
        if isinstance(variables, list):
            self.variables = variables
        elif isinstance(variables, Variable):
            self.variables = [variables]
        else:
            self.variables = []

    def get_iterations(self):
        return max([variable.get_iterations() for variable in self.variables])

    def compatible_iterations(self, other: Variable) -> bool:
        if len(self.variables) == 0:
            return True
        if self.get_iterations() == 1:
            return True
        if other.get_iterations() == 1:
            return True
        return self.get_iterations() == len(other.values)

    def __add__(self, other: Variable | VariablesList):
        if isinstance(other, VariablesList):
            return VariablesList(self.variables + other.variables)
        if not self.compatible_iterations(other):
            raise ValueError(f"cannot parse variable {other.name}: variables must have the same number of values or be single")
        if other.name in [variable.name for variable in self.variables]:
            raise NameError(f"cannot parse variable {other.name}: variable with this name already exists")
        return VariablesList(self.variables + [other])

    def __radd__(self, other: Variable):
        if not self.compatible_iterations(other):
            raise ValueError(f"cannot parse variable {other.name}: variables must have the same number of values or be single")
        if other.name in [variable.name for variable in self.variables]:
            raise NameError(f"cannot parse variable {other.name}: variable with this name already exists")
        return VariablesList(self.variables + [other])

    def get_dict(self, iteration: int) -> dict[str, UFloat]:
        return {variable.name: variable.get_value(iteration) for variable in self.variables}

    def get_centrals_list(self, variable_name: str) -> list[float]:
        return [self.get_dict(iteration)[variable_name].n for iteration in range(self.get_iterations())]

    def get_uncertainties_list(self, variable_name: str) -> list[float]:
        return [self.get_dict(iteration)[variable_name].std_dev for iteration in range(self.get_iterations())]


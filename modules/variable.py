from __future__ import annotations
from uncertainties import UFloat
import numpy as np
import ast

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
        return f"{np.format_float_positional(value.n)} ± {np.format_float_positional(value.std_dev)}"

class VariablesList:

    def __init__(self, variables: list[Variable] | Variable | None =None):
        if isinstance(variables, list):
            self.variables = variables
        elif isinstance(variables, Variable):
            self.variables = [variables]
        else:
            self.variables = []

    def __add__(self, other: Variable | VariablesList):
        if isinstance(other, VariablesList):
            return VariablesList(self.variables + other.variables)
        if other.name in [variable.name for variable in self.variables]:
            raise NameError(f"cannot parse variable {other.name}: variable with this name already exists")
        return VariablesList(self.variables + [other])

    def __radd__(self, other: Variable):
        if other.name in [variable.name for variable in self.variables]:
            raise NameError(f"cannot parse variable {other.name}: variable with this name already exists")
        return VariablesList(self.variables + [other])

    def get_dict(self, iteration: int) -> dict[str, UFloat]:
        return {variable.name: variable.get_value(iteration) for variable in self.variables}

    def get_expression_dict(self, iteration: int, expression: ast.Expression) -> dict[str, UFloat]:
        used_variable_names = [node.id for node in ast.walk(expression) if isinstance(node, ast.Name)]
        return {
                    variable.name: variable.get_value(iteration)
                    for variable in self.variables if variable.name in used_variable_names
                }

    def get_centrals_list(self, variable_name: str) -> list[float]:
        return [
                    self.get_dict(iteration)[variable_name].n
                    for iteration in range(self.get_variable(variable_name).get_iterations())
                ]

    def get_uncertainties_list(self, variable_name: str) -> list[float]:
        return [
                    self.get_dict(iteration)[variable_name].std_dev 
                    for iteration in range(self.get_variable(variable_name).get_iterations())
                ]

    def get_variable(self, variable_name: str) -> Variable:
        try:
            return [variable for variable in self.variables if variable.name == variable_name][0]
        except IndexError:
            raise SyntaxError(f"variable with name {variable_name} does not exist")

    def iterations_of_expression(self, expression: ast.Expression) -> int:
        used_variable_names = [node.id for node in ast.walk(expression) if isinstance(node, ast.Name)]
        non_single_used_variables = [
                                        self.get_variable(variable_name) 
                                        for variable_name in used_variable_names
                                        if self.get_variable(variable_name).get_iterations() != 1
                                    ]
        if not all(
                        [
                            variable.get_iterations() == non_single_used_variables[0].get_iterations()
                            for variable in non_single_used_variables
                        ]
                    ):
            raise SyntaxError("cannot parse expression with non single variables with different iterations")
        if len(non_single_used_variables) == 0:
            return 1
        return non_single_used_variables[0].get_iterations()


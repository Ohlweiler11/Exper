from uncertainties import UFloat, ufloat
from uncertainties.umath import sqrt, exp, sin, cos, tan, log, fabs
from math import pi
import numpy as np
import matplotlib
import tkinter as tk
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import json

class Variable:

    def __init__(self, name: str, unit: str):
        if IndexOfVariable(name) != "Not in list":
            raise NameError(f"variable with name {name} already exists")
        self.name = name
        self.unit = unit
        self.values = []
        self.isSingle = True

    def __str__(self):
        return self.name + self.unit + " : " + str(self.values)

    def name_and_unit(self) -> str:
        return self.name + "(" + self.unit + ")"

    def add_value(self, value: UFloat):
        global experimentIterations
        self.values.append(value)
        experimentIterations = max(experimentIterations, len(self.values))
        if len(self.values) > 1:
            self.isSingle = False
        
    def ValueOfIndex(self, index):
        if readError:
            if self.isSingle:
                return self.values[0]
            return self.values[index]
        if self.isSingle:
            return self.values[0].n
        return self.values[index].n
    
    def CentralsList(self):
        valuesList = []
        for i in range(len(self.values)):
            valuesList.append(self.values[i].n)
        return valuesList
    
    def ErrorsList(self):
        errorsList = []
        for i in range(len(self.values)):
            errorsList.append(self.values[i].std_dev)
        return errorsList
    
    def FormatedValue(self, index):
        value = self.values[index]
        if value.std_dev == float("inf"):
            return str(value.n).replace(".", ",")
        strError = np.format_float_positional(value.std_dev)
        significantAlgarism = "#"
        for i in range(len(strError)):
            if strError[i] == ".":
                point = i
            elif strError[i] != "0" and significantAlgarism == "#": 
                significantAlgarism = i
        if significantAlgarism != "#":
            decimals = significantAlgarism - point
            if decimals < 0:
                central = int(round(value.n, 0))
                error = int(round(value.std_dev, 0))
                return f"{central} ± {error}"
            central = np.format_float_positional(round(value.n, decimals),
                                                 min_digits=decimals, fractional=True, trim='k')
            error = np.format_float_positional(round(value.std_dev, decimals),
                                               min_digits=decimals, fractional=True, trim='k')
            return f"{central.replace('.', ',')} ± {error.replace('.', ',')}"
        return f"{str(value.n).replace('.', ',')} ± 0"

# variablesList  = []
# experimentIterations = 0
# readError = True
# label = "Iteração"
# sheetID = "" # https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0
# readingModesList = ["Variables", "Equations", "Graphs", "Functions"]

def sum_errors(error_1: float, error_2: float) -> float:
    return sqrt(error_1 * error_1 + error_2 * error_2)

def analog_error(interval: float) -> float:
    return interval / (2 * sqrt(6))

def digital_error(interval: float) -> float:
    return interval / (2 * sqrt(3))

def IsSubstringAtIndex(index, string, substring):
    if len(substring) + index > len(string):
        return False
    for i in range(len(substring)):
        if string[i+index] != substring[i]:
            return False
    return True

def SubstringAtIndex(index, string, substringsList):
    for substring in substringsList:
        if IsSubstringAtIndex(index, string, substring):
            return substring  
    return None

def CreateVariableSingleValue(name, unit, central, error):
    value = variable(name, unit)
    value.AddValue(ufloat(central, error))
    variablesList.append(value)

def IndexOfVariable(name):
    for i in range(len(variablesList)):
        if variablesList[i].name == name:
            return i
    return "Not in list"

def code_float(value: str) -> float:
    return float(value.replace(",", "."))

def variable_options(tokens: list) -> dict:
    token_index = 0
    options = {}
    while token_index < len(tokens):
        token = tokens[token_index]
        next_token = tokens[token_index + 1]
        if token[0] != "-":
            token_index += 1
            continue
        option = tokens.pop(token_index)
        match option[1:]:
            case "u":
                options["unit"] = next_token
            case "a":
                options["analog uncertainty"] = float(next_token)
            case "d":
                options["digital uncertainty"] = float(next_token)
            case "%":
                options["percentage uncertainty"] = float(next_token)
            case "*":
                options["factor"] = float(next_token)
            case _:
                raise SyntaxError(f"option {option[1:]} does not exist")
        token_index += 2
    return options

def get_error(base_error: float, central_value: float, options: dict) -> float:
    error = base_error;
    if "analog uncertainty" in options.keys():
        interval = options["analog uncertainty"]
        error = sum_errors(error, analog_error(interval))
    if "digital uncertainty" in options.keys():
        interval = options["digital uncertainty"]
        error = sum_errors(error, digital_error(interval))
    if "percentage uncertainty" in options.keys():
        percentage = options["percentage uncertainty"] * central_value
        error = sum_errors(error, percentage)
    return error


def read_variable(line: str) -> Variable:
    tokens = line.split()
    name = tokens.pop(0)
    options = variable_options(tokens)
    variable = Variable(name, options["unit"])
    for value in tokens:
        has_base_error = "~" in value
        base_error = 0
        if has_base_error:
            central, base_error = map(float, value.split("~"))
        else:
            central = float(value)
        variable.add_value(ufloat(central, get_error(base_error, central, options)))
    return variable

def PythonEquation(line):
    equation = ""
    lastWasVariableOrNumber = False
    isSingleEquation = True
    i = 0
    doBreak = False
    while i < len(line):
        function = SubstringAtIndex(i, line, ["sqrt", "exp", "sin", "cos", "tan", "log", "fabs"])
        if function != None:
            if lastWasVariableOrNumber:
                equation += "*"
            equation += function
            lastWasVariableOrNumber = False
            i += len(function)
            continue
        for variable in variablesList:  
            if IsSubstringAtIndex(i, line, variable.name):
                if not variable.isSingle:
                    isSingleEquation = False
                if lastWasVariableOrNumber:
                    equation += "*"
                equation += variable.name
                lastWasVariableOrNumber = True
                i += len(variable.name)
                doBreak = True
                break
        if doBreak:
            doBreak = False
            continue
        if line[i] == "π":
            if lastWasVariableOrNumber:
                equation += "*"
            equation += "pi"
            lastWasVariableOrNumber = True
        elif line[i] == "²":
            equation += "**2"
            lastWasVariableOrNumber = True
        elif line[i] in map(str, range(0, 10)):
            equation += line[i]
            lastWasVariableOrNumber = True
        elif line[i] == "(" and lastWasVariableOrNumber:
            equation += "*("
            lastWasVariableOrNumber = False
        elif line[i] == ")":
            equation += ")"
            lastWasVariableOrNumber = True
        else:
            equation += line[i]
            lastWasVariableOrNumber = False
        i += 1
    return (equation, isSingleEquation)

def VariablesDictionary(index, xLinspace=None, xVariable=None):
    if xVariable == None:
        dictionary = {
            "exp": exp,
            "sin": sin,
            "cos": cos,
            "tan": tan,
            "log": log,
            "sqrt": sqrt,
            "fabs": fabs
            }
    else:
        dictionary = {
            "exp": np.exp,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "log": np.log,
            "sqrt": np.sqrt,
            "fabs": np.fabs
            }
    dictionary[xVariable] = xLinspace
    for variable in variablesList:
        dictionary[variable.name] = variable.ValueOfIndex(index)
    return dictionary

def EvaluatedEquation(line, variableName, variableUnit):
    currentVariable = variable(variableName, variableUnit)
    equation, isSingleEquation = PythonEquation(line)
    if isSingleEquation:
        currentVariable.AddValue(eval(equation, {}, VariablesDictionary(0)))
        return currentVariable
    for index in range(experimentIterations):
        currentVariable.AddValue(eval(equation, {}, VariablesDictionary(index)))
    return currentVariable

def ReadEquation(line):
    nameAndUnit, equation = line.split("=")
    variableName, variableUnit = nameAndUnit.split("(")
    variableUnit = variableUnit[:-1]
    variablesList.append(EvaluatedEquation(equation, variableName, "(" + variableUnit))

def yFunction(x, A, B):
    return A*x + B

def yFunctionNoB(x, A):
    return A*x

def GaussFunction(x, s, m, y0):
    return (1 / (s*sqrt(2*pi))) * exp(-(x - m)**2 / (2*s*s)) + y0

def LorentzFunction(x, A, x0, G, y0):
    return A / (1 + ((x - x0) / G)**2) + y0

def PlotGraph(xName, xVariable, yName, yVariable):
    plt.xlabel(xName[1:-1], fontsize=axisFontSize)
    plt.ylabel(yName[:-1], fontsize=axisFontSize)
    plt.title(f"Gráfico {yVariable} x {xVariable}", fontsize=titleFontSize)
    plt.legend(fontsize=legendFontSize)
    plt.grid(True)
    plt.show()

def ReadPointsGraph(line):
    yName, xName = line.split("x")
    yFormula = yName.split("(")[0]
    xFormula = xName.split("(")[0][1:]
    yy = EvaluatedEquation(f"{yFormula}", "yy", "()")
    xx = EvaluatedEquation(f"{xFormula}", "xx", "()")
    plt.figure(figsize=graphSize)
    plt.errorbar(xx.CentralsList(), yy.CentralsList(), xerr=xx.ErrorsList(), yerr=yy.ErrorsList(), 
                fmt='o', capsize=5, label="Dados experimentais com incerteza")
    PlotGraph(xName, xFormula, yName, yFormula)

def ReadLinearGraph(line):
    FunctionName, coeficientNames = line.split(":")
    yName, xName = FunctionName.split("x")
    yFormula = yName.split("(")[0]
    xFormula = xName.split("(")[0][1:]
    yy = EvaluatedEquation(f"{yFormula}", "yy", "()")
    xx = EvaluatedEquation(f"{xFormula}", "xx", "()")
    coeficientNames = coeficientNames.split()
    plt.figure(figsize=graphSize)
    if coeficientNames[1] != "0":
        nameA, unitA = coeficientNames[0].split("(")
        nameB, unitB = coeficientNames[1].split("(")
        centrals, errors = curve_fit(yFunction, xx.CentralsList(), yy.CentralsList(),
                                     sigma=yy.ErrorsList(), absolute_sigma=True)
        centralA, centralB = centrals
        errorA, errorB = np.sqrt(np.diag(errors))
        xFit = np.linspace(min(xx.CentralsList()), max(xx.CentralsList()), 100)
        yFit = yFunction(xFit, centralA, centralB)
        CreateVariableSingleValue(nameA, "(" + unitA, centralA, errorA)
        CreateVariableSingleValue(nameB, "(" + unitB, centralB, errorB)
        plt.errorbar(xx.CentralsList(), yy.CentralsList(), xerr=xx.ErrorsList(), yerr=yy.ErrorsList(), 
                fmt='o', capsize=5, label="Dados experimentais com incerteza")
        plt.plot(xFit, yFit, 'r--', label=f"Reta de ajuste linear")
        PlotGraph(xName, xFormula, yName, yFormula)
        return
    nameA, unitA = coeficientNames[0].split("(")
    centrals, errors = curve_fit(yFunctionNoB, xx.CentralsList(), yy.CentralsList(), sigma=yy.ErrorsList(), absolute_sigma=True)
    centralA = centrals[0]
    centralB = 0
    errorA = np.sqrt(np.diag(errors))
    xFit = np.linspace(min(xx.CentralsList()), max(xx.CentralsList()), 100)
    yFit = yFunction(xFit, centralA, centralB)
    CreateVariableSingleValue(nameA, "(" + unitA, centralA, errorA)
    plt.errorbar(xx.CentralsList(), yy.CentralsList(), xerr=xx.ErrorsList(), yerr=yy.ErrorsList(), 
                fmt='o', capsize=5, label="Dados experimentais com incerteza")
    plt.plot(xFit, yFit, 'r--', label=f"Reta de ajuste linear")
    PlotGraph(xName, xFormula, yName, yFormula)

def ReadGaussGraph(line):
    FunctionName, coeficientNames, interval = line.split(":")
    yName, xName = FunctionName.split("x")
    yFormula = yName.split("(")[0]
    xFormula = xName.split("(")[0][1:]
    yy = EvaluatedEquation(f"{yFormula}", "yy", "()")
    xx = EvaluatedEquation(f"{xFormula}", "xx", "()")
    plt.figure(figsize=graphSize)
    coeficientNames = coeficientNames.split()
    nameM, unitM = coeficientNames[0].split("(")
    if interval != " ":
        interval = interval.split("<")
        mask = [float(interval[0]) <= x <= float(interval[1]) for x in xx.CentralsList()]
        xValuesList = [x for x, m in zip(xx.CentralsList(), mask) if m]
        xErrorsList = [x for x, m in zip(xx.ErrorsList(), mask) if m]
        yValuesList = [y for y, m in zip(yy.CentralsList(), mask) if m]
        yErrorsList = [y for y, m in zip(yy.ErrorsList(), mask) if m]
    else:
        xValuesList = xx.CentralsList()
        xErrorsList = xx.ErrorsList()
        yValuesList = yy.CentralsList()
        yErrorsList = yy.ErrorsList()
    dy = abs(max(yValuesList) - min(yValuesList))
    dx = abs(max(xValuesList) - min(xValuesList))
    lowerLimit = [-dy, min(xValuesList), 0, min(yValuesList)]
    upperLimit = [dy, max(xValuesList), dx, max(yValuesList)]
    centrals, errors = curve_fit(GaussFunction, xValuesList, yValuesList,
                                 bounds=(lowerLimit, upperLimit), sigma=yErrorsList, absolute_sigma=True)
    centralA, centralS, centralM, centralY0 = centrals
    errorA, errorS, errorM, errorY0 = np.sqrt(np.diag(errors))
    xFit = np.linspace(min(xValuesList), max(xValuesList), 100)
    CreateVariableSingleValue(nameM, "(" + unitM, centralM, centralS/sqrt(len(xValuesList)))
    yFit = GaussFunction(xFit, centralA, centralS, centralM)
    plt.errorbar(xValuesList, yValuesList, xerr=xErrorsList, yerr=yErrorsList, 
            fmt='o', capsize=5, label="Dados experimentais com incerteza")
    plt.plot(xFit, yFit, 'r--', label=f"Gaussiana de ajuste")
    PlotGraph(xName, xFormula, yName, yFormula)

def ReadLorentzGraph(line):
    FunctionName, coeficientNames, interval = line.split(":")
    yName, xName = FunctionName.split("x")
    yFormula = yName.split("(")[0]
    xFormula = xName.split("(")[0][1:]
    yy = EvaluatedEquation(f"{yFormula}", "yy", "()")
    xx = EvaluatedEquation(f"{xFormula}", "xx", "()")
    plt.figure(figsize=graphSize)
    coeficientNames = coeficientNames.split()
    nameX0, unitX0 = coeficientNames[0].split("(")
    nameG, unitG = coeficientNames[1].split("(")
    if interval != " ":
        interval = interval.split("<")
        mask = [float(interval[0]) <= x <= float(interval[1]) for x in xx.CentralsList()]
        xValuesList = [x for x, m in zip(xx.CentralsList(), mask) if m]
        xErrorsList = [x for x, m in zip(xx.ErrorsList(), mask) if m]
        yValuesList = [y for y, m in zip(yy.CentralsList(), mask) if m]
        yErrorsList = [y for y, m in zip(yy.ErrorsList(), mask) if m]
    else:
        xValuesList = xx.CentralsList()
        xErrorsList = xx.ErrorsList()
        yValuesList = yy.CentralsList()
        yErrorsList = yy.ErrorsList()
    dy = abs(max(yValuesList) - min(yValuesList))
    dx = abs(max(xValuesList) - min(xValuesList))
    lowerLimit = [-dy, min(xValuesList), 0, min(yValuesList)]
    upperLimit = [dy, max(xValuesList), dx, max(yValuesList)]
    centrals, errors = curve_fit(LorentzFunction, xValuesList, yValuesList,
                                 bounds=(lowerLimit, upperLimit), sigma=yErrorsList, absolute_sigma=True)
    centralA, centralX0, centralG, centralY0 = centrals
    errorA, errorX0, errorG, errorY0 = np.sqrt(np.diag(errors))
    xFit = np.linspace(min(xValuesList), max(xValuesList), 100)
    yFit = LorentzFunction(xFit, centralA, centralX0, centralG, centralY0)
    CreateVariableSingleValue(nameX0, "(" + unitX0, centralX0, centralG/sqrt(len(xValuesList)))
    CreateVariableSingleValue(nameG, "(" + unitG, centralG, errorG)
    plt.errorbar(xValuesList, yValuesList, xerr=xErrorsList, yerr=yErrorsList, 
            fmt='o', capsize=5, label="Dados experimentais com incerteza")
    plt.plot(xFit, yFit, 'r--', label=f"Lorentziana de ajuste")
    PlotGraph(xName, xFormula, yName, yFormula)

def ReadGraph(line):
    if line[:6] == "Linear":
        ReadLinearGraph(line[8:])
    elif line[:5] == "Gauss":
        ReadGaussGraph(line[7:])
    elif line[:7] == "Lorentz":
        ReadLorentzGraph(line[9:])
    else:
        ReadPointsGraph(line)

def PlotEvaluatedGraph(x, xName, xVariable, yName, yVariable, equation, index):
    plt.figure(figsize=graphSize)
    y = eval(equation, {}, VariablesDictionary(index, x, xVariable))
    plt.plot(x, y, label=f"Gráfico {yVariable} x {xVariable}")
    PlotGraph(xName, xVariable, yName, yVariable)

def ReadFunction(line):
    FunctionName, yFormula, interval = line.split(":")
    yName, xName = FunctionName.split("x")
    xVariable = xName.split("(")[0]
    yVariable = yName.split("(")[0]
    equation, isSingleEquation = PythonEquation(yFormula)
    interval = interval.split("<")
    global readError
    readError = False
    x = np.linspace(float(interval[0]), float(interval[1]))
    if isSingleEquation:
        PlotEvaluatedGraph(x, xName, xVariable[1:], yName, yVariable, equation, 0)
        return
    for i in range(experimentIterations):
        PlotEvaluatedGraph(x, xName, xVariable[1:], yName, yVariable, equation, i)
    readError = True    

def read_command(line: str, reading_mode: str, variables_list: list) -> str:
    is_reading_mode_declaration = line[-2] == ":"
    if line == "\n" or line[0] == "#":
        return reading_mode
    elif is_reading_mode_declaration:
        return line[:-2]
    elif reading_mode == "":
        raise SyntaxError("invalid section name")
    elif line[:5] == "Sheet":
        global sheetID
        sheetID = line.split()[1]
    elif line[:5] == "Label":
        global label
        label = line.split()[1]
    elif reading_mode == "Variables":
        read_variable(line)
    elif reading_mode == "Equations":
        ReadEquation(line)
    elif reading_mode == "Graphs":
        ReadGraph(line)
    elif reading_mode == "Functions":
        ReadFunction(line)
    return reading_mode

def read_data(data_file: str) -> list:
    variables_list = []
    with open(data_file, "r") as file:
        reading_mode = ""
        for i, line in enumerate(file):
            try:
                reading_mode = read_command(line, reading_mode, variables_list)
            except Exception as error:
                print(f"\nError in line {i+1} of Data.txt\n")
                raise error
    return variables_list

def print_results(variables_list: list, iteration_name: str):
    for variable in variables_list:
        name_and_nit = variable.name + variable.unit
        if variable.isSingle:
            formatedVariable = variable.FormatedValue(0)
            print(f"{nameAndUnit} : {formatedVariable}")
        else:
            print(f"{iteration_name} : {nameAndUnit}")
            for j in range(len(variable.values)):
                formatedVariable = variable.FormatedValue(j)
                print(f"{j+1} : {formatedVariable}")

def main():
    with open("Settings.json", "r") as file:
        settings = json.load(file)
        data_file = settings["Data file"]
        graph_size = tuple(map(float, settings["Graph size"].split()))
        title_font_size = settings["Title size"]
        axis_font_size = settings["Axes size"]
        legend_font_size = settings["Legend size"]
        iteration_name = settings["Iteration name"]
    variables_list = read_data(data_file)
    print_results(variables_list, iteration_name)
    try:
        from sheetswriter import WriteResults
        WriteResults(variables_list, label, sheetID)
    except:
        print("SheetsWriter.py module not used\n")

if __name__ == "__main__":
    main()    

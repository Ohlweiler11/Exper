from uncertainties import *
from uncertainties.umath import sqrt, exp, sin, cos, tan, log, pow, fabs
from math import pi
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import json

class variable:

    def __init__(self, name, unit):
        if IndexOfVariable(name) != "Not in list":
            raise NameError(f"variable with name {name} already exists")
        self.name = name
        self.unit = unit
        self.values = []
        self.isSingle = True

    def __str__(self):
        return self.name + self.unit + " : " + str(self.values)

    def AddValue(self, value):
        if not isinstance(value, UFloat):
            raise ValueError("value must be ufloat")
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
            central = np.format_float_positional(round(value.n, decimals), min_digits=decimals, fractional=True, trim='k')
            error = np.format_float_positional(round(value.std_dev, decimals), min_digits=decimals, fractional=True, trim='k')
            return f"{central.replace(".", ",")} ± {error.replace(".", ",")}"
        return f"{str(value.n).replace(".", ",")} ± 0"

variablesList  = []
experimentIterations = 0
readError = True
label = "Iteração"
sheetID = "" # https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0
readingModesList = ["Variables", "Equations", "Graphs", "Functions"]

def IsSubstringAtIndex(index, string, substring):
    for i in range(len(substring)):
        try:
            if string[i+index] != substring[i]:
                return False
        except:
            return True
    return True

def SubstringAtIndex(index, string, substringsList):
    for substring in substringsList:
        isSubstring = True
        isSubstring = IsSubstringAtIndex(index, string, substring)
        if isSubstring:
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

def Unformat(value):
    return float(value.replace(",", "."))

def ReadVariable(line):
    parameters, values = line.split(":")
    parameters = parameters.split()
    name, unit = parameters.pop(0).split("(")
    multiplier = 1
    generalError = ""
    errorIsPercentage = False
    for i in range(len(parameters)):
        if parameters[i][0] == "*":
            multiplier = Unformat(parameters[i][1:])
        elif parameters[i][1] == "a":
            generalError = Unformat(parameters[i][2:])/(2*sqrt(6))
        elif parameters[i][1] == "d":
            generalError = Unformat(parameters[i][2:])/(2*sqrt(3))
        elif parameters[i][-1] == "%":
            errorIsPercentage = True
            generalError = Unformat(parameters[i][1:-1])
        else:
            generalError = Unformat(parameters[i][1:])
    if not "-" in values and generalError == "":
        raise ValueError(f"missing uncertainties of {name}")
    currentVariable = variable(name, "(" + unit)
    values = values.split()
    if errorIsPercentage:
        for i in range(len(values)):
            value = multiplier * ufloat(Unformat(values[i]), (Unformat(values[i])*generalError)/100)
            currentVariable.AddValue(value)
        variablesList.append(currentVariable)
        return
    if generalError != "":
        for i in range(len(values)):
            value = multiplier * ufloat(Unformat(values[i]), generalError)
            currentVariable.AddValue(value)
        variablesList.append(currentVariable)
        return
    for i in range(len(values)):
        try:
            central, error = values[i].split("-")
            central = Unformat(central)
            error = Unformat(error)
            value = multiplier * ufloat(central, error)
            currentVariable.AddValue(value)
        except ValueError:
            raise ValueError(f"missing uncertainty {i+1} of {name}")
    variablesList.append(currentVariable)

def PythonEquation(line):
    equation = ""
    lastWasVariableOrNumber = False
    isSingleEquation = True
    i = 0
    while i < len(line):
        function = SubstringAtIndex(i, line, ["sqrt", "exp", "sin", "cos", "tan", "log", "pow", "fabs"])
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
    if xLinspace == None:
        dictionary = {
            "exp": np.exp,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "log": np.log,
            "sqrt": np.sqrt,
            "pow": np.power,
            "fabs": np.fabs
            }
    else:
        dictionary = {
            "exp": exp,
            "sin": sin,
            "cos": cos,
            "tan": tan,
            "log": log,
            "sqrt": sqrt,
            "pow": pow,
            "fabs": fabs
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
    FunctionName, sizeRatio = line.split(":")
    yName, xName = FunctionName.split("x")
    yFormula = yName.split("(")[0]
    xFormula = xName.split("(")[0][1:]
    yy = EvaluatedEquation(f"{yFormula}", "yy", "()")
    xx = EvaluatedEquation(f"{xFormula}", "xx", "()")
    sizeRatio = sizeRatio.split("x")
    plt.figure(figsize=(float(sizeRatio[0]),float(sizeRatio[1])))
    plt.errorbar(xx.CentralsList(), yy.CentralsList(), xerr=xx.ErrorsList(), yerr=yy.ErrorsList(), 
                fmt='o', capsize=5, label="Dados experimentais com incerteza")
    PlotGraph(xName, xFormula, yName, yFormula)

def ReadLinearGraph(line):
    FunctionName, coeficientNames, sizeRatio = line.split(":")
    yName, xName = FunctionName.split("x")
    yFormula = yName.split("(")[0]
    xFormula = xName.split("(")[0][1:]
    yy = EvaluatedEquation(f"{yFormula}", "yy", "()")
    xx = EvaluatedEquation(f"{xFormula}", "xx", "()")
    coeficientNames = coeficientNames.split()
    sizeRatio = sizeRatio.split("x")
    plt.figure(figsize=(float(sizeRatio[0]),float(sizeRatio[1])))
    if coeficientNames[1] != "0":
        nameA, unitA = coeficientNames[0].split("(")
        nameB, unitB = coeficientNames[1].split("(")
        centrals, errors = curve_fit(yFunction, xx.CentralsList(), yy.CentralsList(), sigma=yy.ErrorsList(), absolute_sigma=True)
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
    FunctionName, coeficientNames, interval, sizeRatio = line.split(":")
    yName, xName = FunctionName.split("x")
    yFormula = yName.split("(")[0]
    xFormula = xName.split("(")[0][1:]
    yy = EvaluatedEquation(f"{yFormula}", "yy", "()")
    xx = EvaluatedEquation(f"{xFormula}", "xx", "()")
    sizeRatio = sizeRatio.split("x")
    plt.figure(figsize=(float(sizeRatio[0]),float(sizeRatio[1])))
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
    centrals, errors = curve_fit(GaussFunction, xValuesList, yValuesList, bounds=(lowerLimit, upperLimit), sigma=yErrorsList, absolute_sigma=True)
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
    FunctionName, coeficientNames, interval, sizeRatio = line.split(":")
    yName, xName = FunctionName.split("x")
    yFormula = yName.split("(")[0]
    xFormula = xName.split("(")[0][1:]
    yy = EvaluatedEquation(f"{yFormula}", "yy", "()")
    xx = EvaluatedEquation(f"{xFormula}", "xx", "()")
    sizeRatio = sizeRatio.split("x")
    plt.figure(figsize=(float(sizeRatio[0]),float(sizeRatio[1])))
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
    centrals, errors = curve_fit(LorentzFunction, xValuesList, yValuesList, bounds=(lowerLimit, upperLimit), sigma=yErrorsList, absolute_sigma=True)
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

def PlotEvaluatedGraph(x, xName, xVariable, yName, yVariable, equation, index, sizeRatio):
    from numpy import sqrt, exp, sin, cos, tan, log, pow, fabs
    plt.figure(figsize=(float(sizeRatio[0]),float(sizeRatio[1])))
    y = eval(equation, {}, VariablesDictionary(index, x, xVariable))
    plt.plot(x, y, label=f"Gráfico {yVariable} x {xVariable}")
    PlotGraph(xName, xVariable, yName, yVariable)

def ReadFunction(line):
    FunctionName, yFormula, interval, sizeRatio = line.split(":")
    yName, xName = FunctionName.split("x")
    xVariable = xName.split("(")[0]
    yVariable = yName.split("(")[0]
    equation, isSingleEquation = PythonEquation(yFormula)
    interval = interval.split("<")
    sizeRatio = sizeRatio.split("x")
    global readError
    readError = False
    x = np.linspace(float(interval[0]), float(interval[1]))
    if isSingleEquation:
        PlotEvaluatedGraph(x, xName, xVariable[1], yName, yVariable, equation, 0, sizeRatio)
        return
    for i in range(experimentIterations):
        PlotEvaluatedGraph(x, xName, xVariable[1], yName, yVariable, equation, i, sizeRatio)
    readError = True    

def ReadCommand(line, readingMode):
    if line == "\n" or line[0] == "#":
        return readingMode
    elif line[:-2] in readingModesList:
        readingMode = line[:-2]
    elif readingMode == "":
        raise SyntaxError("invalid section name")
    elif line[:5] == "Sheet":
        global sheetID
        sheetID = line.split()[1]
    elif line[:5] == "Label":
        global label
        label = line.split()[1]
    elif readingMode == "Variables":
        ReadVariable(line)
    elif readingMode == "Equations":
        ReadEquation(line)
    elif readingMode == "Graphs":
        ReadGraph(line)
    elif readingMode == "Functions":
        ReadFunction(line)
    return readingMode

def ReadData(dataFile):
    with open(dataFile, "r") as file:
        readingMode = ""
        for i, line in enumerate(file):
            try:
                readingMode = ReadCommand(line, readingMode)
            except Exception as error:
                print(f"\nError in line {i+1} of Data.txt\n")
                raise error

def PrintResults():
    for variable in variablesList:
        nameAndUnit = variable.name + variable.unit
        if variable.isSingle:
            formatedVariable = variable.FormatedValue(0)
            print(f"{nameAndUnit} : {formatedVariable}")
        else:
            print(f"{label} : {nameAndUnit}")
            for j in range(len(variable.values)):
                formatedVariable = variable.FormatedValue(j)
                print(f"{j+1} : {formatedVariable}")

if __name__ == "__main__":
    with open("Settings.json", "r") as file:
        settings = json.load(file)
        dataFile = settings["dataFile"]
        titleFontSize = settings["titleFontSize"]
        axisFontSize = settings["axisFontSize"]
        legendFontSize = settings["legendFontSize"]
    ReadData(dataFile)
    PrintResults()
    try:
        from SheetsWriter import WriteResults
        WriteResults(variablesList, label, sheetID)
    except:
        print("SheetsWriter.py module not used\n")

from uncertainties import *
from uncertainties.umath import sqrt, exp, sin, cos, tan, log, pow, fabs
from math import pi
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from gspread_formatting import cellFormat, format_cell_ranges
from pathlib import Path

titleFontSize = 20
axisFontSize = 20
legendFontSize = 20
dataFile = "Data.txt"

class variable:

    def __init__(self, name, unit):
        if len(name) > 1 and name != "yy" and name != "xx":
            raise NameError(f"variable name must be single letter (cannot be {name})")
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
sheet = []
label = "Label"
sheetID = "" # https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0

def CreateVariableSingleValue(name, unit, central, error):
    value = variable(name, unit)
    value.AddValue(ufloat(central, error))
    variablesList.append(value)

def IndexOfVariable(name):
    for i in range(len(variablesList)):
        if variablesList[i].name == name:
            return i
    return "Not in list"

def unformat(value):
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
            multiplier = unformat(parameters[i][1:])
        elif parameters[i][1] == "a":
            generalError = unformat(parameters[i][2:])/(2*sqrt(6))
        elif parameters[i][1] == "d":
            generalError = unformat(parameters[i][2:])/(2*sqrt(3))
        elif parameters[i][-1] == "%":
            errorIsPercentage = True
            generalError = unformat(parameters[i][1:-1])
        else:
            generalError = unformat(parameters[i][1:])
    if not "-" in values and generalError == "":
        raise ValueError(f"missing uncertainties of {name}")
    currentVariable = variable(name, "(" + unit)
    values = values.split()
    if errorIsPercentage:
        for i in range(len(values)):
            value = multiplier * ufloat(unformat(values[i]), (unformat(values[i])*generalError)/100)
            currentVariable.AddValue(value)
        variablesList.append(currentVariable)
        return
    if generalError != "":
        for i in range(len(values)):
            value = multiplier * ufloat(unformat(values[i]), generalError)
            currentVariable.AddValue(value)
        variablesList.append(currentVariable)
        return
    for i in range(len(values)):
        try:
            central, error = values[i].split("-")
            central = unformat(central)
            error = unformat(error)
            value = multiplier * ufloat(central, error)
            currentVariable.AddValue(value)
        except ValueError:
            raise ValueError(f"missing uncertainty {i+1} of {name}")
    variablesList.append(currentVariable)

def PythonEquation(line, substituteForX=""):
    equation = ""
    lastWasVariable = False
    isSingleEquation = True
    for i in range(len(line)):
        isVariable = IndexOfVariable(line[i]) != "Not in list"
        if line[i] == substituteForX and lastWasVariable:
            equation += "*xx"
        elif line[i] == substituteForX:
            equation += "xx"
        elif isVariable:
            if lastWasVariable or line[i-1] in map(str, range(10)):
                equation += "*"
            lastWasVariable = True
            equation += f"variablesList[IndexOfVariable(\"{line[i]}\")].ValueOfIndex(index)"
            if not variablesList[IndexOfVariable(line[i])].isSingle:
                isSingleEquation = False
        elif line[i] == "π":
            equation += "pi"
            lastWasVariable = True
        elif line[i] == "²" and line[i-1] == substituteForX:
            equation += "*xx"
            lastWasVariable = True
        elif line[i] == "²":
            equation += f"*variablesList[IndexOfVariable(\"{line[i-1]}\")].ValueOfIndex(index)"
            lastWasVariable = True
        else:
            equation += line[i]
            lastWasVariable = False
    return (equation, isSingleEquation)

def EvaluatedEquation(line, variableName, variableUnit):
    currentVariable = variable(variableName, variableUnit)
    equation, isSingleEquation = PythonEquation(line)
    if isSingleEquation:
        index = 0
        currentVariable.AddValue(eval(equation))
        return currentVariable
    for index in range(experimentIterations):
        currentVariable.AddValue(eval(equation))
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
        interval = interval.split("-")
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
        interval = interval.split("-")
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

def PlotEvaluatedGraph(xx, xName, xVariable, yName, yVariable, equation, index, sizeRatio):
    plt.figure(figsize=(float(sizeRatio[0]),float(sizeRatio[1])))
    yy = eval(equation)
    plt.plot(xx, yy, label=f"Gráfico {yVariable} x {xVariable[1]}")
    PlotGraph(xName, xVariable, yName, yVariable)

def ReadFunction(line):
    from numpy import sqrt, exp, sin, cos, tan, log, pow, fabs
    FunctionName, yFormula, interval, sizeRatio = line.split(":")
    yName, xName = FunctionName.split("x")
    xVariable = xName.split("(")[0]
    yVariable = yName.split("(")[0]
    equation, isSingleEquation = PythonEquation(yFormula, xVariable[1])
    interval = interval.split("-")
    sizeRatio = sizeRatio.split("x")
    global readError
    readError = False
    x = np.linspace(float(interval[0]), float(interval[1]))
    if isSingleEquation:
        PlotGraph(x, xName, xVariable[1], yName, yVariable, equation, 0, sizeRatio)
        return
    for i in range(experimentIterations):
        PlotGraph(x, xName, xVariable[1], yName, yVariable, equation, i, sizeRatio)
    readError = True    

def ReadCommand(line):
    global readingMode
    if line == "\n" or line[0] == "#":
        return
    elif line[:5] == "Sheet":
        sheetID = line.split()[1]
    elif line[:5] == "Label":
        label = line.split()[1]
    elif line[:-2] in readingModesList:
        readingMode = line[:-2]
    elif readingMode == "":
        raise SyntaxError("invalid section name")
    elif readingMode == "Variables":
        ReadVariable(line)
    elif readingMode == "Equations":
        ReadEquation(line)
    elif readingMode == "Graphs":
        ReadGraph(line)
    elif readingMode == "Functions":
        ReadFunction(line)

with open(dataFile, "r") as file:
    readingModesList = ["Variables", "Equations", "Graphs", "Functions"]
    readingMode = ""
    for i, line in enumerate(file):
        try:
            ReadCommand(line)
        except Exception as error:
            print(f"\nError in line {i+1} of Data.txt\n")
            raise error

for i in range(len(variablesList)):
    currentVariable = variablesList[i]
    nameAndUnit = currentVariable.name + currentVariable.unit
    if currentVariable.isSingle:
        formatedVariable = currentVariable.FormatedValue(0)
        sheet.append((nameAndUnit, formatedVariable))
        print(f"{nameAndUnit} : {formatedVariable}")
    else:
        sheet.append((label, nameAndUnit))
        print(f"{label} : {nameAndUnit}")
        for j in range(len(currentVariable.values)):
            formatedVariable = currentVariable.FormatedValue(j)
            sheet.append((j+1, formatedVariable))
            print(f"{j+1} : {formatedVariable}")

def jsonInDirectory():
    for file in scriptDirectory.iterdir():
        if file.suffix == ".json":
            return file.name

if sheetID != "":
    df = pd.DataFrame(sheet)
    df = df.astype(str)
    scriptDirectory = Path(__file__).resolve().parent
    credentials = Credentials.from_service_account_file(jsonInDirectory(),
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_key(sheetID)
    worksheet = sheet.sheet1
    fmt = cellFormat(horizontalAlignment='LEFT')
    format_cell_ranges(worksheet, [('A1:Z1000', fmt)])
    set_with_dataframe(worksheet, df, include_column_header=False)
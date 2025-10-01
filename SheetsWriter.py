import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from gspread_formatting import cellFormat, format_cell_ranges
from pathlib import Path

sheet = []

def jsonInDirectory():
    scriptDirectory = Path(__file__).resolve().parent
    for file in scriptDirectory.iterdir():
        if file.suffix == ".json":
            return file.name

def WriteResults(variablesList, label, sheetID):
    for i in range(len(variablesList)):
        currentVariable = variablesList[i]
        nameAndUnit = currentVariable.name + currentVariable.unit
        if currentVariable.isSingle:
            formatedVariable = currentVariable.FormatedValue(0)
            print(f"{nameAndUnit} : {formatedVariable}")
        else:
            sheet.append((label, nameAndUnit))
            for j in range(len(currentVariable.values)):
                formatedVariable = currentVariable.FormatedValue(j)
                sheet.append((j+1, formatedVariable))
    if sheetID != "":
        df = pd.DataFrame(sheet)
        df = df.astype(str)
        credentials = Credentials.from_service_account_file(jsonInDirectory(),
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_key(sheetID)
        worksheet = sheet.sheet1
        fmt = cellFormat(horizontalAlignment='LEFT')
        format_cell_ranges(worksheet, [('A1:Z1000', fmt)])
        set_with_dataframe(worksheet, df, include_column_header=False)

            
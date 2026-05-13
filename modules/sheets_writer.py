from modules.variable import Variable, VariablesList
import modules.settings_getter as settings_getter
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from gspread_formatting import CellFormat, format_cell_ranges
from pathlib import Path

def write_results(variables: VariablesList) -> None:
    dataframe = pd.DataFrame(results_sheet(variables)).astype(str)
    credentials = Credentials.from_service_account_file(
                                                            service_account_json(),
                                                            scopes=
                                                                    [
                                                                        "https://www.googleapis.com/auth/spreadsheets", 
                                                                        "https://www.googleapis.com/auth/drive"
                                                                    ]
                                                        )
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(settings_getter.get_sheet_id())
    worksheet = sheet.sheet1
    format_cell_ranges(worksheet, [('A1:Z1000', CellFormat(horizontalAlignment='LEFT'))])
    set_with_dataframe(worksheet, dataframe, include_column_header=False)

def service_account_json() -> str | None:
    main_directory = Path(__file__).resolve().parent.parent
    for file in main_directory.iterdir():
        if file.suffix == ".json" and file.name != "settings.json":
            return file.name
    return None

def results_sheet(variables: VariablesList) -> list[tuple[str, str]]:
    return results_sheet_recursion(variables, 0, 0)
    
def results_sheet_recursion(variables: VariablesList, variable_index: int, iteration: int) -> list[tuple[str, str]]:
    if variable_index == variables.length():
        return []
    if iteration > 0:
        if iteration == variables.get(variable_index).get_iterations():
            return []
        return [
                    (str(iteration + 1), variables.get(variable_index).formatted_value(iteration))
                ] + results_sheet_recursion(variables, variable_index, iteration + 1)
    if variables.get(variable_index).get_iterations() == 1:
        return [
                    (variables.get(variable_index).name_and_unit(), variables.get(variable_index).formatted_value(0))
                ] + results_sheet_recursion(variables, variable_index + 1, 0)
    else:
        return [
                    (settings_getter.get_iteration_name(), variables.get(variable_index).name_and_unit()),
                    ("1", variables.get(variable_index).formatted_value(0))
                ] + results_sheet_recursion(
                                                variables, 
                                                variable_index,
                                                1
                ) + results_sheet_recursion(
                                                variables,
                                                variable_index + 1,
                                                0
                                            )

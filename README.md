
A tool for uncertainty calculation, graph plotting and funtion approximation for experimental science

## Installation
To use the base functionalities of Exper, you need to download:
- exper.py
- settings.json

The following python libraries:
- uncertainties
- numpy
- matplotlib
- scipy

And:
- python3-tk

Or simply:
```console
wget https://github.com/Ohlweiler11/Exper/blob/main/exper.py
wget https://github.com/Ohlweiler11/Exper/blob/main/settings.json
pip install uncertainties numpy matplotlib scipy
sudo apt install python3-tk
```
Or the apropriate command to install python3-tk for your distro.

In case pip does not work, create a venv to install the libraries and run the program:
```console
python3 -m venv .venv
```

## Usage
To use Exper you will have to create a file named "Data.txt" in the same directory as Exper.py and write commands in it. Commands are written inside sections. To open a section you need to write the name of the section followed by ":". Lines starting with "\n" or "#" are ignored. For example:
```
Variables:
*variable command here*

# Here is an ignored line
```
Here are the sections and their commands:

### Variables

```
var *name* *value_1*~*uncertainty_1 *value_2*~*uncertainty_2* *value_3*~*uncertainty_3* ...
[--u=unit] [--g=uncertainty] [--a=interval] [--d=interval] [--%=percentage] [--*=factor]
```

### Equations
```
eqn *variable* *formula*
[--u=unit]
```

### Points Graphs

```
ptg *y_formula* *x_formula*
[--uy=unit] [--ux=unit] [--la=a_variable] [--ula=unit] [--lb=a_variable] [--ulb=unit]
```

### Function Graphs

```
```

## Additional settings
Some settings can also be modified in the Setttings.json file:
- Data file: name of the data file read (useful for using multiple data files within the same directory)
- Graph size: length and height of ploted graphs
- Title size: font size of titles in graphs
- Axes size: font size of x and y axes names in graphs
- Legend size: font size of legend in graphs

## Google Sheets integration
Exper can also write values, results and uncertainties tables automatically to Google Sheets. To use the Google Sheets integration, you will need to download SheetsWriter.py and the following python libraries:
- pandas
- gspread
- gspread-dataframe
- gspread-formatting
- google-auth

Or simply:
```console
pip install pandas gspread gspread-dataframe gspread-formatting google-auth
```

And follow these steps:
- Create a google cloud project and enable Google Sheets API
- Create a service account
- Download its JSON key and put it in the Exper directory
- Share the Google Sheet with the service account email
- Write "Key: " in the Data.txt file followed by the key of the Google Sheets spreadsheet (https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0) and run Exper.py

You can also write "Label: \*label name*" in Data.txt to specify a name for the iterations of the experiment to be written in Sheets.

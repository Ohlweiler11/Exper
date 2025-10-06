# Exper
Tool for uncertainty calculation, graph plotting and funtion approximation for experimental science

_Don't forget to add Exper to your references!_

## Installation
To use the base functionalities of Exper, you need to download:
- Exper.py
- Data.txt
- Settings.json

And the following python libraries:
- uncertainties
- numpy
- matplotlib
- scipy

## Usage
To use Exper you will have to write commands in Data.txt. Commands are written inside sections. To open a section you need to write the name of the section followed by ":". Lines starting with "\n" or "#" are ignored. For example:
```
Variables:
*variable command here*

# Here is an ignored line
```
Here are the sections and their commands:

### Variables
Creates variables from values. Variables are written like this:
```
Name(unit) : value1-uncertainty1 value2-uncertainty2 value3-uncertainty3 ...
```
Each value of a variable with multiple values is interpreted as the value for an iteration of the experiment.
After the name and the unit, there are also optional parameters: *_x_ (multipies all values with uncertainties by _x_) and -_x_ (makes _x_ the uncertainty for every value). The general uncertainty can also be written as -_ax_, -_dx_ (interpreting _x_ as the interval for a analog or digital uncertainty) or -_x_% (making the uncertainty a percentage of the value). For example:
```
Variables:
d(m) *0.01 -a0.1 : 0.0 1.2 2.3 3.1
t(s) : 0.0-0.1 1.0-0.2 2.1-0.1 2.9-0.3
m(kg) *0.001 : 25-5
```

### Equations
Calculates variables from other variables. Equations are written like this:
```
Name(unit) = *expression from other variables*
```
The expression is interpretend as pyhon syntax, but also accepts "π", "²" and concatenated terms for multiplication.
The new variable is calculated for each iteration of the variables if at least one of them has multiple values. Values for a certain iteration are calculated using the values of the other variables for this iteration. For example:
```
Equations:
v(m/s) = d/t
p(Ns) = mv
```
Following the previous example, _v_ is created with 4 values, one for each respective value of _d_ and _t_. After that, _p_ is created with 4 values, one for each respective value of _v_, with all of them using the only _m_ value.

### Graphs
Plots graphs with points of values. Graphs are written like this:
```
yVariable(unit) x xVariable(unit)
```
For example:
```
d(m) x t(s)
```
#### Function approximation
Graphs can also be used to approximate a function based on the points:
```
*Approximation name*: yVariable(unit) x xVariable(unit) : parameter1(unit) parameter2(unit) : value1<value2
```
Fitting a function in the interval [value1, value2] and creating variables with the parameters of the resulting function. These are the approximation options:
- Linear: Ax + B (parameters: A B)
- Gauss: gaussian (parameters: μ)
- Lorentz: lorentzian (parameters: x_0 Γ)

For example:
```
Linear: v(m/s) x t(s) : a(m/s²) v0(m/s)
```

### Functions
Plots graphs based on a function. Functions are written like this:
```
yVariable(unit) x xVariable(unit) : *expression as a function of xVariable* : value1<value2
```
Creating a graph of that expression within the interval [value1, value2] of xVariable. For example:
```
Ec(J) x t(s) : m(a*t + v0)²/2 : 0<20
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
- google-auth

And follow these steps:
- Create a google cloud project and enable Google Sheets API
- Create a service account
- Download its JSON key and put it in the Exper directory
- Share the Google Sheet with the service account email
- Write "Key: " in the Data.txt file followed by the key of the Google Sheets spreadsheet (https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0) and run Exper.py

You can also write "Label: \*label name*" in Data.txt to specify a name for the iterations of the experiment to be written in Sheets.

## Author
Made by Henrique Ohlweiler
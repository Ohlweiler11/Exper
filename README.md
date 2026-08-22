# Exper
A tool for uncertainty calculation, graph plotting and funtion approximation for experimental science

## Installation
To use the base functionalities of Exper, you need to download, into the same directory:
- exper.py
- modules/*
- settings.json

The following python libraries:
- uncertainties
- numpy
- matplotlib
- scipy

And:
- python3-tk

## Usage
To use Exper you will have to create a file named "data.txt" in the same directory as Exper.py and write commands in it.
Lines starting with '#' and '\n' are ignored. Options (--...) can be written on any order.

Here are the possible commands:

### var

Creates a variable based on values.
Creates variable *variable* with values *central_1*±*uncertainty_1*, *central_2*±*uncertainty_2*, *central_3*±*uncertainty_3*...
multiplied by *factor* with unit *unit*.
Uncertainties are combined with general *uncertainty*, analog of interval *analog*,
digital of interval *digital* and *percentage*% of each value.

```markdown
var *variable* *central_1*~*uncertainty_1 *central_2*~*uncertainty_2* *central_3*~*uncertainty_3* ...
[--u=*unit*] [--g=*uncertainty*] [--a=*analog*] [--d=*digital*] [--%=*percentage*] [--*=*factor*]
```

### eqn

Creates a variable based on a equation.
Creates variable *variable* with unit *unit* with values calculated by *formula*.
*formula* must be in python syntax and can use numbers and other variables.
All variables used must either have one value or a constant n number or values, since values are calculated by index.
Therefore *variable* will also have n values, each calculated using the values of each used variable for the respective index.

```markdown
eqn *variable* *formula*
[--u=*unit*]
```

### ptg

Creates a graph with points.
y values for the points are based on *y_formula* with unit *y_unit* and x values are based on *x_formula* with unit *x_unit*.
If options --la and/or --lb are specified, a linear regression (y = a*x + b) will be made and variables *a_variable*
and *b_variable* will be created with those values and units *a_unit* and *b_unit*, respectively. If one of the options is not
specified, it will be considered 0.

```markdown
ptg *y_formula* *x_formula*
[--uy=*y_unit*] [--ux=*x_unit*] [--la=*a_variable*] [--ula=*a_unit*] [--lb=*a_variable*] [--ulb=*b_unit*]
```

### fng

Creates a graph based on a funciton.
Creates a graph of y = *formula*, with axes named *y_name* and *x_name* and units *y_unit* and *x_unit*.
*fomula* must follow the same rules as *formula* in eqn.

```markdown
fng *y_name* *x_name* *formula*
[--uy=*y_unit*] [--ux=*x_unit*]
```

## Additional settings

Some settings can also be modified in the setttings.json file.

## Google Sheets integration
Exper can also write values, results and uncertainties tables automatically to Google Sheets. To use the Google Sheets integration, you will need to download SheetsWriter.py and the following python libraries:
- pandas
- gspread
- gspread-dataframe
- gspread-formatting
- google-auth

And follow these steps:
- Create a google cloud project and enable Google Sheets API
- Create a service account
- Download its JSON key and put it in the Exper directory
- Share the Google Sheet with the service account email
- Write "Key: " in the Data.txt file followed by the key of the Google Sheets spreadsheet (https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0) and run Exper.py

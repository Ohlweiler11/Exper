# Exper
Tool for uncertainty calculation, graph plotting and funtion approximation for experimental science

## If you are reading this, this readme is not finished yet.

## Installation
To use the base functionalities of Exper, you need to download Exper.py, Data.txt and Settings.json.

## Usage
To use Exper you will have to write commands in Data.txt. Commands are written inside sections. To open a section you need to write the name of the section followed by ":". Lines starting with "\n" or "#" are ignored. For exemple:
```
Variables:
_variable command here_

# Here is an ignored line
```
Here are the sections and their commands:

### Variables
Creates variables from values. Variables are written like this:
```
Name(unit) : _value1-uncertainty1 value2-uncertainty2 value3-uncertainty3_ ...
```
Each value of a variable with multiple values is interpreted as the value for an iteration of the experiment.
After the name and the unit, there are also optional parameters: *_x_ (multipies all values with uncertainties by _x_) and -_x_ (makes _x_ the uncertainty for every value). The general uncertainty can also be written as -_ax_, -_dx_ (interpreting _x_ as the interval for a analog or digital uncertainty) or -_x_% (making the uncertainty a percentage of the value). For example:
```
Variables:
d(m) *0.01 -a0.1 : 10.1 11.9 14.3 16.0
t(s) : 5.0-0.1 5.9-0.2 8.2-0.1 10.0-0.3
m(kg) *0.001 : 25-5
```
### Equations
Calculates variables from other variables. Equations are written like this:
```
Name(unit) = _operation of other variables_
```
The operation is interpretend as pyhon syntax, but also accepts "π", "²" and concatenated terms for multiplication.
The new variable is calculated for each iteration of the variables if at least one of them has multiple values. Values for a certain iteration are calculated using the values of the other variables for this iteration. For example:
```
Equations:
v(m/s) = d/t
p(Ns) = mv
```
Following the previous example, _v_ is created with 4 values, one for each respective value of _d_ and _t_. After that, _p_ is created with 4 values, one for each respective value of _v_, with all of them using the only _m_ value.

### Graphs
Creates graphs with points of values. Can also approximate those points to a function. Graphs are written like this:



### Functions

## Additional settings

## Google Sheets Integration

## Author
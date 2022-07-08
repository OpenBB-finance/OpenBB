```
usage: exe [-p PATH] [-i ROUTINE_ARGS] [-h]
```

The .openbb scripts offer the ability to automatically run a set of commands in the form of a **routine**. Furthermore,
the scripts can be adapted, and documented, at any moment giving the user full control over the type of analysis you wish
to do (and repeat). This can fundamental research, understanding market movements, finding hidden gems and even
doing advanced statistical/econometric research.

```
optional arguments:
  -p PATH, --path PATH  The path or .openbb file to run. (default: )
  -i ROUTINE_ARGS, --input ROUTINE_ARGS
                        Select multiple inputs to be replaced in the routine and separated by commas. E.g. GME,AMC,BTC-USD (default: None)
  -h, --help            show this help message (default: False)

```

An example of a script can be the following (inside a `.openbb` file):

```
# Go into the econometrics context
econometrics

# Load the wage_panel dataset and include an alias
load wage_panel -a wp

# Set the MultiIndex, allowing for Panel regressions to be performed
index wp -i nr,year

# Change the type of the year column so it can be included as time effects within the regressions
type wp.year -f category

# Perform a Pooled OLS, Random Effects and Fixed Effects estimation
panel -d wp.lwage -i wp.black,wp.hisp,wp.exper,wp.expersq,wp.married,wp.educ,wp.union,wp.year
panel -d wp.lwage -i wp.black,wp.hisp,wp.exper,wp.expersq,wp.married,wp.educ,wp.union,wp.year -r re
panel -d wp.lwage -i wp.expersq,wp.union,wp.married,wp.year -r fe

# Compare the results obtained from these regressions
compare
```
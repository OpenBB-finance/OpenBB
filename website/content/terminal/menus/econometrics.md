---
title: Econometrics
description: This documentation page introduces the Econometrics menu, in the OpenBB Terminal.  The menu has features for performing statistical analysis on custom datasets.
keywords:
- econometrics
- statistics
- statistical research
- custom datasets
- panel regression
- autocorrelation tests
- heteroscedasticity
- OpenBBUserData
- panel
- normality
- co-integration
- unitroot
- garch
- linear regression
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Econometrics - Menus | OpenBB Terminal Docs" />

The Econometrics functions are for performing statistical analysis on custom datasets.  Multiple data sets can be loaded from local storage and modified with basic DataFrame operations. Statistical tests - (e.g. <a href="https://en.wikipedia.org/wiki/Breusch%E2%80%93Godfrey_test" target="_blank" rel="noreferrer noopener">Breusch-Godfrey autocorrelation tests</a>) or OLS and Panel regressions (e.g. <a href="https://en.wikipedia.org/wiki/Random_effects_model" target="_blank" rel="noreferrer noopener">Random Effects</a> and <a href="https://en.wikipedia.org/wiki/Fixed_effects_model" target="_blank" rel="noreferrer noopener">Fixed Effects</a>) - are performed on any of the loaded files.

## Usage

Enter the Econometrics menu from the main menu by typing, `econometrics`, into the Terminal.  The absolute path for the menu is:

```console
/econometrics
```

![Screenshot 2023-11-02 at 9 03 24 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/b1720a35-d5d0-44c8-9826-b0cfffe29ee0)


### Sample Datasets

![Screenshot 2023-11-02 at 12 12 07 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/44cf93ce-96f9-4c6b-bed1-611f27738de9)

There are sample datasets included in the Scipy library, those are listed by adding `--examples` to the `load` command. For example, `longley`:

```console
load longley
```

:::note
Due to the small size of the dataset, many of these tests are not statistically significant.
:::


### Load

The first step in using the Econometrics menu is to load in some data.  Place files in the paths displayed at the top of the menu, under "Looking for data in:".

![Screenshot 2023-11-02 at 9 15 17 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/aabd6f32-2495-45f4-84b7-3d6686875e66)

This file contains historical monthly levels of the S&P 500 price and P/E ratio.  It was populated from: [Nasdaq Data Link](https://data.nasdaq.com/data/MULTPL-sp-500-ratios).

After loading a file, refreshing the screen (`?` or `h` with no command) updates the information printed under "Loaded files and data columns:".

```console
Loaded files and data columns:
        sp500_pe : date, pe, price
```

### Show

Use the `show` command to inspect a a loaded file.  If more than one file has been loaded, specify the target's name.

```console
show sp500_pe
```

| date       |    pe |   price |
|:-----------|------:|--------:|
| 1871-01-31 | 11.1  |    4.44 |
| 1871-02-28 | 11.25 |    4.5  |
| ...        | ...   |    ...  |
| 2023-10-31 | 23.94 | 4193.8  |


### Index

Set the index by using a similar syntax to:

```console
index sp500_pe -i date
```

A confirmation message will print:

```console
Successfully updated 'sp500_pe' index to be 'date'
```

### Type

Format any column as one of:

- int
- float
- str
- bool
- cataegory
- date

To see what a column is defined as already:

```console
type sp500_pe.pe
```

```console
The type of 'sp500_pe.pe' is 'float64'
```

Change it by adding the `--format` argument and one of the choices listed above.

If this column of numbers was defined as a string, it could be changed with:

```console
type -n sp500_pe.pe --format float
```

```console
Update 'sp500_pe.pe' with type 'float'
```

### RET

Add a column to the time series for returns.

```console
ret -v sp500_pe.price
```

### Clean

If NaN values exist, use the `clean` command to handle them.  The example below removes rows where they exist.  The new `returns` column will contain a NaN in the first row.

```console
clean sp500_pe -d rdrop
```

```console
Successfully cleaned 'sp500_pe' dataset
```

### Plot

Plot columns from a loaded dataset using the `plot` command.

```console
plot sp500_pe.pe
```

![Screenshot 2023-11-02 at 9 40 47 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/316104d9-17a7-4c96-9516-57a4074fd221)

### OLS

Fit an OLS regression model to a loaded data set by defining the dependent and independent variables as column names.

```console
ols sp500_pe.pe -i sp500_pe.price,sp500_pe.price_returns
```

![Screenshot 2023-11-02 at 11 15 11 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/6ba43577-aa95-4c17-b1d4-77561629972f)

**`bgod` and `bpag` commands require running `OLS` first.**


### Norm

The `norm` is used to determine whether the data is normally distributed.

```console
norm sp500_pe.price_returns
```

|           |   Kurtosis |   Skewness |   Jarque-Bera |   Shapiro-Wilk |   Kolmogorov-Smirnov |
|:----------|-----------:|-----------:|--------------:|---------------:|---------------------:|
| Statistic |    20.5784 |    7.20623 |       20258.4 |       0.903374 |             0.454473 |


A histogram of the distribution is displayed by adding a, `-p`, flag to the command.

```console
norm sp500_pe.price_returns -p
```

![Screenshot 2023-11-02 at 12 25 22 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/4aa0ff4a-b3c5-4a88-acd5-25c754724b9f)


### Working With Panel Data

Within the examples of `load --examples` there is one panel dataset available named `wage_panel`. This is a dataset from the paper by Vella and M. Verbeek (1998), “Whose Wages Do Unions Raise? A Dynamic Model of Unionism and Wage Rate Determination for Young Men,” Journal of Applied Econometrics 13, 163-183. This is a well-known dataset also used within Chapter 14 of <a href="https://www.amazon.com/Introductory-Econometrics-Modern-Approach-Economics/dp/1111531048" target="_blank" rel="noreferrer noopener">Introduction to Econometrics by Jeffrey Wooldridge</a>.

In the example below, the dataset is loaded and given an alias by adding the, `-a`, argument.

```console
/econometrics/load --file wage_panel -a wp
```

To run panel regressions, it is important to define both _entity_ (e.g. company) and _time_ (e.g. year). Trying to run the `panel` command would right now result in the following:

```console
panel -d wp.lwage -i wp.black,wp.hisp,wp.exper,wp.expersq,wp.married,wp.educ,wp.union,wp.year
```

```console
The column 'lwage' from the dataset 'wp' is not a MultiIndex.

Make sure you set the index correctly with the index (e.g. index wp -i lwage,nr) command where the first level is the entity (e.g. Tesla Inc.) and the second level the date (e.g. 2021-03-31)
```

Within this dataset the `nr` and `year` columns define the _entity_ and _time_. To allow panel regression estimations, they will need to be defined using the `index` command.

```console
index wp -i nr,year
```

```console
Successfully updated 'wp' index to be 'nr, year'
```

The columns `nr` and `year` still exists within the dataset and could have been dropped with the `-d` argument if desired. However, in this case the `year` column is relevant for generating time effects in Pooled OLS, Fixed Effects and Random Effects estimations. To be able to do this, the type of the year column needs to be changed.

For the panel regressions, it can be beneficial to see time effects from `year`. Therefore, the type of the `year` column should be altered to `category`. This can be done with the following command:

```console
type wp.year --format category
```

```console
Update 'wp.year' with type 'category'
```

The dataset is now properly configured to allow for proper panel regressions.  The type of regression used is a choice of:

- `-r pols` (Pooled OLS)
- `-r re` (Random Effects)
- `-r bols` (Between OLS)
- `-r fe` (Fixed Effects)
- `-r fdols` (First Difference OLS).

For example, a **Random Effects** regression is performed.

```
panel -d wp.lwage -i wp.black,wp.hisp,wp.exper,wp.expersq,wp.married,wp.educ,wp.union,wp.year -r re
```

![Screenshot 2023-11-02 at 1 03 57 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/1b576690-53b6-4ca2-9aa7-bc19cb3ac4f1)


### Scripts & Routines

Doing research, both as a student or professor for a university or as a professional, often requires the findings to be easily replicated. As many steps could be required, the ability to make small adjustments without needing to re-do every single step again. This is where [OpenBB Routines](/terminal/usage/routines/introduction-to-routines.md) play an important role.

Use the contents below as a demo file, copying and pasting into a file saved to the `~/OpenBBUserData/routines` folder.

```txt
# Go into the econometrics context
econometrics

# Load the wage_panel dataset and include an alias
load wage_panel -a wp

# Set the MultiIndex, allowing for Panel regressions to be performed
index wp -i nr,year

# Change the type of the year column so it can be included as time effects within the regressions
type wp.year --format category

# Perform a Pooled OLS, Random Effects and Fixed Effects estimation
panel -d wp.lwage -i wp.black,wp.hisp,wp.exper,wp.expersq,wp.married,wp.educ,wp.union,wp.year
panel -d wp.lwage -i wp.black,wp.hisp,wp.exper,wp.expersq,wp.married,wp.educ,wp.union,wp.year -r re
panel -d wp.lwage -i wp.expersq,wp.union,wp.married,wp.year -r fe

# Compare the results obtained from these regressions
compare
```

Run the routine from the Main menu:

```console
/exe -f name_of_file.openbb
```

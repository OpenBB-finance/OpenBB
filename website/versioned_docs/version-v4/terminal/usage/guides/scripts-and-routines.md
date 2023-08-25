---
sidebar_position: 4
title: Scripts & Routines
description: Learn how to set up and maintain scripts and routines in the OpenBB Terminal. These operations will help automate processes and repetitive tasks to save time and effort.
keywords: [scripts, routines, .do file, stata, spss, r studio, python, automation, data collection, aggregation, script, routine, openbb terminal, tasks, processes]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Scripts & Routines - Terminal | OpenBB Docs" />

OpenBB Routine Scripts allow users to write simple scripts for automating processes and repetitive tasks. In essence these are text plain-text files that can be created or modified in any basic text editor with the only difference of having an `.openbb` extension.

Other software like STATA, SPSS and R-Studio share similar functionality in the area of Econometrics and the OpenBB routine scripts venture into the area of financial analysis and data collection to speed up the process.

For example, not only is it possible to automate a set of functionality, it is also possible to export a large amount of data to Excel through the usage of `--export` and `--sheet-name` making data collection efficient, reproducible and customizable.

## Introduction

Run a routine file from the main menu, with the `exe` command. A great start would be to use `exe --example` to get a sense of what this functionality does. Below, the `--help` dialogue is displayed.

```console
usage: exe [--file PATH] [-i ROUTINE_ARGS] [-e] [-h]

Execute automated routine script. For an example, please use `exe --example` and for documentation and to learn how create your own script type `about exe`.

options:
  --file PATH           The path or .openbb file to run. (default: None)
  -i ROUTINE_ARGS, --input ROUTINE_ARGS
                        Select multiple inputs to be replaced in the routine and separated by commas. E.g. GME,AMC,BTC-USD (default: None)
  -e, --example         Run an example script to understand how routines can be used. (default: False)
  -h, --help            show this help message (default: False)
```

## The Macro Recorder

OpenBB script routines can be captured with the macro recorder, controlled with global commands, `record` to start saving commands and `stop` to terminate the recording. This shares similarities with that of Excel's VBA methods. This means that any command you run will be automatically recorded for the routine script and once you type `stop` it automatically saves the file to the `~/OpenBBUserData/routines/` folder.

For example, if you copy and paste the following prompt in the OpenBB Terminal and press enter, you will see an example.

```console
$ /record/economy/cpi/treasury/index sp500/stop
```

The following shows the output from this pipeline of commands.

![Routines](https://user-images.githubusercontent.com/46355364/223204998-70d9e5da-f84e-4c22-90c4-576dcf87c1df.png)

Because there was a `record` and `stop` at the `start` and `end` respectively, a routine script was created. This file cane be found inside the `routines` folder within the `OpenBBUserData` folder (more on exporting and import data [here](https://docs.openbb.co/terminal/usage/guides/data)).

Now, you should be able to access the routine file from the terminal main menu by doing `/exe --file` and using the auto-completer. Note that the naming of the file will differ for you based on the time you are executing the script.

![Routines](https://user-images.githubusercontent.com/46355364/223205394-77e7a33d-e9fa-4686-b32f-e8d183b265e6.png)

## Basic Script

The most basic script style contains 2 main elements:

  - **Comments**: any text after a hashtag (`#`) is referred to as a comment. This is used to explain what is happening within the line below and is ignored when the file is executed.
  - **Commands**: any text *without* a hashtag is being ran inside the OpenBB Terminal as if the user had prompted that line in the terminal. Note that this means that you are able to create a pipeline of commands in a single line, i.e. `stocks/load AAPL/candle --ma 20` is a valid line for the script.

For instance, the text below corresponds to the example file that OpenBB provides.

```
# Go into the stocks context
stocks

# Load a company ticker, e.g. Apple
load AAPL

# Show a candle chart with a 20 day Moving Average
candle --ma 20

# Switch over to the Fundamental Analysis menu
fa

# Show Earnings per Share (EPS) estimates
epsfc

# Show price targets charts
pt

# Show future estimations
est

# Return to home
home
```

## Creating and Running a Routine Script

As a starting point, let's use the example above.

1. Create a new text file with name `routines_template.openbb` and copy paste the routine above. For simplicity you can also download the template file **[here](https://www.dropbox.com/s/73g9qx9xgtbb2ec/routines_template.openbb?dl=1)**.
2. Move the file inside the `routines` folder within the [OpenBBUserData](https://docs.openbb.co/terminal/usage/guides/data) folder and, optionally, adjust the name to your liking.
3. Open up the OpenBB Terminal, and type `exe --file routines_template`. If you changed the name of the file, then replace `routines_template` by such. As long as the file remains in the `routines` folder, you will be able to find your file through OpenBB Terminal's auto-completer capability.

Now you should expect the contents of the example above to be run. This means that a candle chart with a moving average of 20 days, expectations and price targets from analysts and estimated future performance should pop up before returning to the home window.

![OpenBB Routine Script Execution](https://user-images.githubusercontent.com/46355364/223207167-dfab3a74-d34d-47d4-bf6e-44944e8fbfa2.png)

## Input Variables

The previous example shows the promise of this language. However, it would be exhausting to have to create one file per ticker of interest. And this is why we allow the user to create arguments within a script that will be populated at the time of execution, which provides a more efficient experience.

As an example, let's look into the following routine (the file can be downloaded [here](https://www.dropbox.com/s/usooz6y29r1xldb/routines_template_with_inputs.openbb?dl=1)):

```
# This script requires you to use arguments. This can be done with the following:
# exe --file routines_template_with_inputs.openbb -i TSLA,AAPL,MSFT

# Go to the stocks menu
stocks

# Load a ticker, given the argument used. E.g. -i TSLA
load $ARGV[0]

# Enter the Technical Analysis (ta) menu
ta

# Show the fibonacci retracement levels
fib

# Enter the comparison analysis (ca) menu
../ca

# Set two extra tickers based on the arguments used. E.g. -i TSLA,AAPL,MSFT
add $ARGV[1],$ARGV[2]

# Plot the historical prices
historical

# Return to home
home
```

This script includes `$ARGV[0]`, `$ARGV[1]` and `$ARGV[2]`. This means that the script requires you to submit three arguments. In this case, they refer to <a href="https://www.investopedia.com/ask/answers/12/what-is-a-stock-ticker.asp" target="_blank" rel="noreferrer noopener">stock tickers</a>. Therefore, like the script also says, you can include these arguments with `-i` or `--input` followed by three tickers (e.g. `/exe routines_template_with_inputs.openbb -i TSLA,AAPL,MSFT`). Resulting in the following,

![OpenBB Script with Input](https://user-images.githubusercontent.com/46355364/223207706-42995834-577f-4747-8185-42a016f441d9.png)

Note: Make sure you saved this script in the `~/OpenBBUserData/routines/` folder else you are not able to execute it.

## Set Variables

In addition, OpenBB accepts the creation of variables inside the script. This can be useful when the user utilizes a ticker as a benchmark/reference, and therefore instead of having to change the ticker of interest in multiple places they can just change the variable. Example of script below:

```
# Set date variable
$DATE = 2022-01-01

# Set list of tickers to iterate
$TICKERS = AAPL,MSFT

# dive into stocks
stocks

# candle chart for first ticker
load $TICKERS[0] --start $DATE/candle

# candle chart for second ticker
load $TICKERS[1] --start $DATE[0]/candle
```

Note that a variable can be declared as a single argument `$DATE = 2022-01-01` but it can also be declared as a list `$TICKERS = AAPL,MSFT`.

When declared as a list, the user needs to use the indexing to access the element of interest, i.e. if interested in `MSFT` then `$TICKERS[1]` should be used.

When a single element is defined, then the user can access it through the variable name or indexing the first position equally, i.e. `$DATE` = `$DATE[0]`.

Note that slicing is also possible, and the same convention as python is utilized. If the user has defined inputs `AAPL,MSFT,TSLA,NVDA,GOOG` then by selecting `$ARGV[1:3]` the tickers `MSFT,TSLA` are selected.

## Relative Time Kewyword Variables

:::note
**This functionality requires OpenBB V 3.1.0 or later.**
:::

The previous input variables are very powerful and can be used for a wide range of functionalities - one of them being dates. E.g. a typical example could be running a script routine with `exe myscript -i TSLA,2010-01-01` where `$ARGV[1]=2010-01-01` and thus it denotes an instant of time.

However, what if instead of wanting an absolute date we want a relative date? The OpenBB scripts now have the capability to recognize these. There are 4 main types of keywords:

* **AGO** - this corresponds to a time in the past relative to today. Valid examples are: `$365DAYSAGO`, `$12MONTHSAGO`, `$1YEARSAGO`.

* **FROMNOW** - this corresponds to a time in the future relative to today. Valid examples are: `$365DAYSFROMNOW`, `$12MONTHSFROMNOW`, `$1YEARSFROMNOW`.

* **LAST** - this refers to the last specific day of the week or month that has occurred. Valid examples are: `$LASTMONDAY`, `$LASTJUNE`.

* **NEXT** - this refers to the next specific day of the week or month that will occur. Valid examples are: `$NEXTFRIDAY`, `$NEXTNOVEMBER`.

The result will be a date with the conventional date associated with OpenBB, i.e. `YYYY-MM-dd`.

## Foreach Loop

:::note
**This functionality requires OpenBB V 3.1.0 or later.**
:::

To be a powerful scripting language, we needed to introduce the concept of foreach loops. These allows to iterate through a list of variables / arguments to execute a sequence commands.

In order to create a foreach loop all you need to do is:

1. Create the header `foreach $$VAR in X` where `X` can be an argument or a list of variables. Note that the `$$VAR` can take other naming as long as the `$$` convention is kept.

2. Insert commands you are interested in repeating in the following lines

3. Finish with a `end`.

Some valid examples are shown below as reference

```
# Iterates through ARGV elements from position 1 onwards
foreach $$VAR in $ARGV[1:]
    load $$VAR --start $DATES[0] --end $DATES[1]/dps/psi/..
end
```

```
# Loops through all $ARGV variables
FOREACH $$SOMETHING in $ARGV
    load $$SOMETHING --start $DATE[0]/ins/stats/..
 end
```

```
# Iterates through ARGV elements in position 1,2
foreach $$VAR in $ARGV[1:3]
    load $$VAR --start 2022-01-01
    ba
    regions
    ..
END
```

```
# Loops through PLTR and BB
foreach $$X in PLTR,BB
    load $$X --start $LASTJANUARY
    candle
END
```

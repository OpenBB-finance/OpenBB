---
title: Routines for Power Users
sidebar_position: 5
description: This documentation guides on running automated workflows in OpenBB by
  introducing variables and arguments for routines. Explains about input variables,
  relative time keyword variables, internal script variables and creating loops for
  batch execution.
keywords:
- automated workflows
- routines
- arguments
- variables
- relative time keywords
- internal script variables
- loops
- batch execution
- OpenBBTutorial
- Technical Analysis
- Stock Tickers
- Running Scripts
- Executing Commands
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Routines for Power Users - Routines - Usage | OpenBB Terminal Docs" />

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
    youtubeLink="https://www.youtube.com/embed/zhbX5tTmyPw?si=5XzbbhgiCFsTmbDo"
    videoLegend="Short video on what power users can do with routines"
/>

## Input Variables

When utilizing basic routines capabilities, users had to create separate routines for each specific ticker, such as `my_due_diligence_AAPL.openbb` or `my_due_diligence_TSLA.openbb`. This approach was suboptimal, considering that we had control over reading these scripts and they were meant to be used within our ecosystem.

To address this limitation, we introduced the concept of arguments, inspired by the Perl language. These arguments are variables referenced within the `.openbb` script as `$ARGV` or `$ARGV[0]`, `$ARGV[1]`, and so on. They are provided in the terminal when running `exe` by adding the `--input` flag, followed by the variables separated by commas.

For instance, if a routine file called `script_with_input.openbb` had the following format:

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/5b0f558e-ace0-423d-a3db-b6369755cffb)

And we run it in the terminal with `exe —file script_with_input.openbb —input MSFT`, what would be run would be `stocks/load MSFT --start 2015-01-01/ta/ema -l 20,50,100,200` and so you could use the same routine for multiple tickers - **making it a more powerful automated workflow**.

For instance, the example below shows how you can run the same script for MSFT but also TSLA ticker.

And we run it in the terminal with exe —file script_with_input.openbb —input MSFT, what would be run would be stocks/load MSFT --start 2015-01-01/ta/ema -l 20,50,100,200 and so you could use the same routine for multiple tickers - making it a more powerful automated workflow.

For instance, the example below shows how you can run the same script for `MSFT` but also `TSLA` ticker.

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/8a744571-59b9-4293-bdd7-5dd6e2c8eef3)

### Example

Let's look into the following routine (the file can be downloaded [here](https://www.dropbox.com/s/usooz6y29r1xldb/routines_template_with_inputs.openbb?dl=1)):

```bash
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

In addition to enabling users to run scripts with external variables using the keyword `ARGV`, we also support the use of internal variables within the script. These variables are defined by starting with the `$` character.

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/c0cc6e1e-b87c-46f4-8c94-539408745433)

Which has the following output:

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/77060dfc-216e-490f-af72-3d4af5642e0f)

Note that the variable can have a single element or can be constituted by an array where elements are separated using a comma “,”.

### Variables Example

Example of the script below:

```bash
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

## Relative Time Keyword Variables

In addition to the powerful variables discussed earlier, OpenBB also supports the usage of relative keywords, particularly for working with dates. These relative keywords provide flexibility when specifying dates about the current day. There are four types of relative keywords:

1. **AGO**: Denotes a time in the past relative to the present day. Valid examples include `$365DAYSAGO`, `$12MONTHSAGO`, `$1YEARSAGO`.

2. **FROMNOW**: Denotes a time in the future relative to the present day. Valid examples include `$365DAYSFROMNOW`, `$12MONTHSFROMNOW`, `$1YEARSFROMNOW`.

3. **LAST**: Refers to the last specific day of the week or month that has occurred. Valid examples include `$LASTMONDAY`, `$LASTJUNE`.

4. **NEXT**: Refers to the next specific day of the week or month that will occur. Valid examples include `$NEXTFRIDAY`, `$NEXTNOVEMBER`.

The result will be a date with the conventional date associated with OpenBB, i.e. `YYYY-MM-DD`.

### Relative Time Example

By picking on the previous example, we can add to the load `--start` argument the keyword `$18MONTHSAGO`.

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/e0e9b4a2-3d8d-4f72-8029-55f009dc15ee)

This will result in the following output:

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/78d6235e-15a1-47cb-a99c-19694b6af0d9)

## Foreach Loop

Finally, what scripting language would this be if there were no loops? For this, we were inspired by MatLab. The loops in OpenBB utilize the foreach and end convention, allowing for iteration through a list of variables or arguments to execute a sequence of commands.

To create a foreach loop, you need to follow these steps:

1. Create the loop header using the syntax: `foreach $$VAR in X` where `X` represents either an argument or a list of variables. It's worth noting that you can choose alternative names for the `$$VAR` variable, as long as the `$$` convention is maintained.

2. Insert the commands you wish to repeat on the subsequent lines.

3. Conclude the loop with the keyword `end`.

### Loop Examples

```bash
# Iterates through ARGV elements from position 1 onwards
foreach $$VAR in $ARGV[1:]
    load $$VAR --start $DATES[0] --end $DATES[1]/dps/psi/..
end
```

```bash
# Loops through all $ARGV variables
FOREACH $$SOMETHING in $ARGV
    load $$SOMETHING --start $DATE[0]/ins/stats/..
 end
```

```bash
# Iterates through ARGV elements in position 1,2
foreach $$VAR in $ARGV[1:3]
    load $$VAR --start 2022-01-01
    ba
    regions
    ..
END
```

```bash
# Loops through PLTR and BB
foreach $$X in PLTR,BB
    load $$X --start $LASTJANUARY
    candle
END
```

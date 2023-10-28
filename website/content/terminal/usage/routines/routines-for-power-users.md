---
title: Routines for Power Users
sidebar_position: 5
description: Learn how to set up and maintain scripts and routines in the OpenBB Terminal. These operations will help automate processes and repetitive tasks to save time and effort.
keywords: [finance, terminal, command line interface, cli, menu, commands]
---

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
    youtubeLink="https://www.youtube.com/embed/zhbX5tTmyPw?si=5XzbbhgiCFsTmbDo"
    videoLegend="Short video on what power users can do with routines"
/>

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

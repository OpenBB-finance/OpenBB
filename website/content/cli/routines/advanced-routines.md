---
title: Advanced Routines
sidebar_position: 5
description: This page provides guidance on creating and running advanced workflows in the OpenBB Platform CLI by
  introducing variables and arguments for routines. It explains input variables,
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
- Tutorial
- Running Scripts
- Executing Commands
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Advanced Routines - Routines | OpenBB Platform CLI Docs" />

## Input Variables

Arguments are variables referenced within the `.openbb` script as `$ARGV` or `$ARGV[0]`, `$ARGV[1]`, and so on. They are provided in the CLI when running `exe` by adding the `--input` flag, followed by the variables separated by commas.

### Example

```text
# This script requires you to use arguments. This can be done with the following:
# exe --file routines_template_with_input.openbb -i TSLA
# Replace the name of the file with your file.

# Navigate to the menu
/equity/price

# Load the data and display a chart
historical --symbol $ARGV --chart
```

## Set Variables

In addition to external variables using the keyword, `ARGV`, internal variables can be defined with the, `$`, character.

Note that the variable can have a single element or can be constituted by an array where elements are separated using a comma “,”.

### Internal Variables Example

```text
# Example routine with internal variables.

$TICKERS = XLE,XOP,XLB,XLI,XLP,XLY,XHE,XLV,XLF,KRE,XLK,XLC,XLU,XLRE

/equity

price

historical --symbol $TICKERS --provider yfinance --start_date 2024-01-01 --chart

home
```

## Relative Time Keyword Variables

In addition to the powerful variables discussed earlier, OpenBB also supports the usage of relative keywords, particularly for working with dates. These relative keywords provide flexibility when specifying dates about the current day. There are four types of relative keywords:

1. **AGO**: Denotes a time in the past relative to the present day. Valid examples include `$365DAYSAGO`, `$12MONTHSAGO`, `$1YEARSAGO`.

2. **FROMNOW**: Denotes a time in the future relative to the present day. Valid examples include `$365DAYSFROMNOW`, `$12MONTHSFROMNOW`, `$1YEARSFROMNOW`.

3. **LAST**: Refers to the last specific day of the week or month that has occurred. Valid examples include `$LASTMONDAY`, `$LASTJUNE`.

4. **NEXT**: Refers to the next specific day of the week or month that will occur. Valid examples include `$NEXTFRIDAY`, `$NEXTNOVEMBER`.

The result will be a date with the conventional date associated with OpenBB, i.e. `YYYY-MM-DD`.

### Relative Time Example

```text
$TICKERS = XLE,XOP,XLB,XLI,XLP,XLY,XHE,XLV,XLF,KRE,XLK,XLC,XLU,XLRE

/equity

price

historical --symbol $TICKERS --provider yfinance --start_date $3MONTHSAGO --chart

..

calendar

earnings --start_date $NEXTMONDAY --end_date $NEXTFRIDAY --provider nasdaq

home
```

## Foreach Loop

Finally, what scripting language would this be if there were no loops? For this, we were inspired by MatLab. The loops in OpenBB utilize the foreach and end convention, allowing for iteration through a list of variables or arguments to execute a sequence of commands.

To create a foreach loop, you need to follow these steps:

1. Create the loop header using the syntax: `foreach $$VAR in X` where `X` represents either an argument or a list of variables. It's worth noting that you can choose alternative names for the `$$VAR` variable, as long as the `$$` convention is maintained.

2. Insert the commands you wish to repeat on the subsequent lines.

3. Conclude the loop with the keyword `end`.

### Loop Example

```text
# Iterates through ARGV elements.
foreach $$VAR in $ARGV[1:]
    /equity/fundamental/filings --symbol $$VAR --provider sec
end
```

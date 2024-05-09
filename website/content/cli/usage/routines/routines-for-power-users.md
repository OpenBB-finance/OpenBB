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

<HeadTitle title="Routines for Power Users - Routines - Usage | OpenBB CLI Docs" />

## Input Variables

Arguments are variables referenced within the `.openbb` script as `$ARGV` or `$ARGV[0]`, `$ARGV[1]`, and so on. They are provided in the CLI when running `exe` by adding the `--input` flag, followed by the variables separated by commas.

### Example

```bash
# This script requires you to use arguments. This can be done with the following:
# exe --file routines_template_with_inputs.openbb -i TSLA,AAPL,MSFT

# Go to the stocks menu
```

## Set Variables

In addition to external variables using the keyword, `ARGV`, internal variables can be defined with the, `$`, character.

Which has the following output:

Note that the variable can have a single element or can be constituted by an array where elements are separated using a comma “,”.

### Variables Example


## Relative Time Keyword Variables

In addition to the powerful variables discussed earlier, OpenBB also supports the usage of relative keywords, particularly for working with dates. These relative keywords provide flexibility when specifying dates about the current day. There are four types of relative keywords:

1. **AGO**: Denotes a time in the past relative to the present day. Valid examples include `$365DAYSAGO`, `$12MONTHSAGO`, `$1YEARSAGO`.

2. **FROMNOW**: Denotes a time in the future relative to the present day. Valid examples include `$365DAYSFROMNOW`, `$12MONTHSFROMNOW`, `$1YEARSFROMNOW`.

3. **LAST**: Refers to the last specific day of the week or month that has occurred. Valid examples include `$LASTMONDAY`, `$LASTJUNE`.

4. **NEXT**: Refers to the next specific day of the week or month that will occur. Valid examples include `$NEXTFRIDAY`, `$NEXTNOVEMBER`.

The result will be a date with the conventional date associated with OpenBB, i.e. `YYYY-MM-DD`.

### Relative Time Example

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
    some_command
end
```

```bash
# Loops through all $ARGV variables
FOREACH $$SOMETHING in $ARGV
    some_sequence
 end
```

```bash
# Iterates through ARGV elements in position 1,2
foreach $$VAR in $ARGV[1:3]
    some_menu
    another_menu
    some_command
    ..
END
```

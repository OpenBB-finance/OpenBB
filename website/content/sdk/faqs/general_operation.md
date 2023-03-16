---
title: General operation
sidebar_position: 3
description: TBD
keywords:
  [
    installation,
    installer,
    install,
    guide,
    mac,
    windows,
    linux,
    python,
    github,
    macos,
    how to,
    explanation,
    openbb terminal,
  ]
---

## General Operation

<details><summary>What is the correct format for entering dates to function variables?</summary>

Dates should be entered as a string variable, inside of quotation marks, formatted as `%Y-%m-%d` - YYYY-MM-DD.

</details>

<details><summary>Does the portfolio menu allow for dividends, interest, or other distributions?</summary>

Currently, this is only possible by manually updating the portfolio file.

</details>

<details><summary>Why does my Portfolio file fail to load?</summary>

This can be the result of a formatting error, check the file in a simple text editor to observe any abnormalities in the formatting; or, it could be a bug - check the [GitHub issues page](https://github.com/OpenBB-finance/OpenBBTerminal/issues) for similar errors.

- Check that all the necessary column titles are present.
- Inspect the file to see if cells left blank have been filled unintentionally with 0 or NaN values.
- A particular asset may not be able to load data. Check for valid historical data from the Stocks menu.
- Format ticker symbols according to yFinance naming convention.
- All dates must be entered as YYYY-MM-DD.
- Transactions dated for today will fail to load historical data.
- MacOS users should attempt to avoid using the Numbers application as it has a habit of changing the formatting while saving.

Files can be formatted as either `.csv` or `.xlsx` files, and the required column headers are:

`[Date,Type,Ticker,Side,Price,Quantity,Fees,Investment,Currency,Sector,Industry,Country,Region]`

See the guide [here](https://docs.openbb.co/sdk/guides/intros/portfolio) for more information.

</details>

<details><summary>How do I change the chart styles?</summary>

Place style sheets in this folder: `OpenBBUserData/styles/user`

To select the light themes:

```python
from openbb_terminal.sdk import TerminalStyle
theme = TerminalStyle("light", "light", "light")
```

To select the dark themes:

```python
from openbb_terminal.sdk import TerminalStyle
theme = TerminalStyle("dark", "dark", "dark")
```

</details>

<details><summary>Where are the included stock screener presets located?</summary>

The files are located in the folder with the code, under:

`~/openbb_terminal/miscellaneous/stocks/screener`

Alternatively, the source code on GitHub is [here](https://github.com/OpenBB-finance/OpenBBTerminal/tree/develop/openbb_terminal/miscellaneous/stocks/screener)

</details>

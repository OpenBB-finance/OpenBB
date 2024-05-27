---
title: Quick Start
sidebar_position: 2
description: This page is a quick start guide for the OpenBB Platform CLI.
keywords:
- quickstart
- quick start
- tutorial
- getting started
- cli
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Quick Start - Usage | OpenBB Platform CLI Docs" />

## Launch

- Open a Terminal and activate the environment where the `openbb-cli` package was installed.
- On the command line, enter: `openbb`

![CLI Home](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/d1617c3b-c83d-4491-a7bc-986321fd7230)

## Login

Login to your [OpenBB Hub account](https://my.openbb.co) to add stored keys to the session.

```console
/account/login --pat REPLACE_WITH_YOUR_PAT
```

:::tip
Add `--remember-me` to the command to persist the login until actively logging out.
:::

Login by email & password is also possible.

```console
/account/login --email my@emailaddress.com --password n0Ts3CuR3L!kEPAT
```

Find all data providers [here](https://docs.openbb.co/platform/extensions/data_extensions), and manage all your credentials directly on the [OpenBB Hub](https://my.openbb.co/app/platform/credentials).

## Menus

:::info
Menus are distinguishable from commands by the character, `>`, on the left of the screen.
:::

Enter a menu by typing it out and pressing return.

```console
economy
```

![Economy Menu](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/b68491fc-d6c3-42a7-80db-bfe2aa848a5a)

### Go Back One Level

Return to the parent menu by entering either:

- `..`
- `q`

### Go Back To Home

Return to the base menu by entering either:

- `/`
- `home`

### Jump Between Menus

Use absolute paths to navigate from anywhere, to anywhere.

From:

```console
/equity/calendar/earnings
```

To:

```console
/economy/calendar
```

## Commands

Commands are displayed on-screen in a lighter colour, compared with menu items, and they will not have, `>`.

Functions have a variety of parameters that differ by endpoint and provider. Use the `--help` dialogue to understand the nuances of any particular command.

### How To Enter Parameters

Parameters are all defined through the same pattern, `--argument`, followed by a space, and then the value.

If the parameter is a boolean (true/false), there is no value to enter. Adding the `--argument` flags the parameter to be the opposite of its default state.

:::danger
The use of positional arguments is not supported.

❌ `historical AAPL --start_date 2024-01-01`

✅ `historical --symbol AAPL --start_date 2024-01-01`
:::

### Use Auto Complete

The auto completion engine is triggered when the spacebar is pressed following any command, or parameter with a defined set of choices.

After the first parameter has been set, remaining parameters will be triggered by entering `--`.

```console
historical --symbol AAPL --start_date 2024-01-01 --
```

![Auto Complete](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/78e68bbd-094e-4558-bce0-92b8d556fcaf)

### Data Processing Commands

Data processing extensions, like `openbb-technical` accept `--data` as an input.

:::info
Command outputs are cached. These can be check using the `results` command and are selected with the `--data` parameter.
:::

```console
# Store the command output
/equity/price/historical --symbol SPY --start_date 2024-01-01 --provider yfinance

# Check results content
results

# Use the results
/technical/rsi --data OBB0 --chart
```

![SPY RSI](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/b480da04-92e6-48e2-bccf-cebc16fb083a)

## Help Dialogues

Display the help dialogue by attaching, `--help` or `-h`, to any command.

:::info
Use this to identify the providers compatible with each parameter, if applicable.
:::

```console
calendar --help
```

```console
usage: calendar [--start_date START_DATE] [--end_date END_DATE] [--provider {fmp,nasdaq,tradingeconomics}] [--country COUNTRY] [--importance {Low,Medium,High}]
                [--group {interest rate,inflation,bonds,consumer,gdp,government,housing,labour,markets,money,prices,trade,business}] [-h] [--export EXPORT]
                [--sheet-name SHEET_NAME [SHEET_NAME ...]]

Get the upcoming, or historical, economic calendar of global events.

options:
  --start_date START_DATE
                        Start date of the data, in YYYY-MM-DD format.
  --end_date END_DATE   End date of the data, in YYYY-MM-DD format.
  --provider {fmp,nasdaq,tradingeconomics}
                        The provider to use for the query, by default None.
                            If None, the provider specified in defaults is selected or 'fmp' if there is
                            no default.
  --country COUNTRY     Country of the event. (provider: nasdaq, tradingeconomics)
  -h, --help            show this help message
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, svg
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files.

tradingeconomics:
  --importance {Low,Medium,High}
                        Importance of the event.
  --group {interest rate,inflation,bonds,consumer,gdp,government,housing,labour,markets,money,prices,trade,business}
                        Grouping of events

```

If the source selected was Nasdaq, `--provider nasdaq`, the `--importance` and `--group` parameters will be ignored.

```console
/economy/calendar --provider nasdaq --country united_states
```

| date                | country       | event                    | actual   | previous   | consensus   | description   |
|:--------------------|:--------------|:-------------------------|:---------|:-----------|:------------|:--------------|
| 2024-05-08 13:30:00 | United States | Fed Governor Cook Speaks | -        | -          | -           |               |
| cont... | | | | | | |

## Export Data

Data can be exported as a CSV, JSON, or XLSX file, and can also be exported directly from the interactive tables and charts.

### Named File

This command exports the Nasdaq directory as a specific CSV file. The path to the file is displayed on-screen.

```console
/equity/search --provider nasdaq --export nasdaq_directory.csv
```

```console
Saved file: /Users/myusername/OpenBBUserData/nasdaq_directory.csv
```

### Unnamed File

If only supplied with the file type, the export will be given a generic name beginning with the date and time.

```console
/equity/search --provider nasdaq --export csv
```

```
Saved file: /Users/myusername/OpenBBUserData/20240508_145308_controllers_search.csv
```

### Specify Sheet Name

Exports can share the same `.xlsx` file by providing a `--sheet-name`.

```console
/equity/search --provider nasdaq --export directory.xlsx --sheet-name nasdaq
```

## Run Multiple Commands

A chain of commands can be run from a single line, separate each process with `/`. The example below will draw two charts and can be pasted as a single line.

```console
/equity/price/historical --symbol AAPL,MSFT,GOOGL,AMZN,META,NVDA,NFLX,TSLA,QQQ --start_date 2022-01-01 --provider yfinance --chart/performance --symbol AAPL,MSFT,GOOGL,AMZN,META,NVDA,NFLX,TSLA,QQQ --provider finviz --chart
```

## Example Routine

To demonstrate how multiple commands are sequenced as a script, try running the example Routine.

```console
/exe --example
```

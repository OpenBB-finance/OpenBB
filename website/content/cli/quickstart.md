---
title: Quick Start
sidebar_position: 2
description: This page is a quick start guide for the OpenBB CLI.
keywords:
- quickstart
- quick start
- tutorial
- getting started
- cli
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Quick Start - Usage | OpenBB CLI Docs" />

## Launch

- Open a Terminal and activate the environment where the `openbb-cli` package was installed.
- On the command line, enter: `openbb`

![CLI Home](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/d1617c3b-c83d-4491-a7bc-986321fd7230)

## Login

Login to your [OpenBB Hub account](https://my.openbb.co) to add your stored keys to the session.

```console
/account/login --pat REPLACE_WITH_YOUR_PAT
```

Login by email & password is also possible.

```console
/account/login --email my@emailaddress.com --password n0Ts3CuR3L!kEPAT
```

:::tip
Add `--remember-me` to the command to persist the login until actively logging out.
:::

## Menus

:::tip
Menus are distinguishable from commands by the character, `>`, on the left of the screen.
:::

Enter a menu by typing it out and pressing return.

```console
economy
```

![Economy Menu](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/b68491fc-d6c3-42a7-80db-bfe2aa848a5a)

## Help Dialogues

Display the help dialogue by attaching, `--help` or `-h`, to any command.

:::tip
Use this to identify the providers compatible with each parameter, if applicable.
:::

```console
calendar --help
```

```bash
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
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg
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

## Jump Between Menus

Use absolute paths to navigate from anywhere, to anywhere.

From:

```console
/equity/calendar/earnings
```

To:

```console
/economy/calendar
```

## Export Data

Data can be exported as a CSV, JSON, or XLSX file.

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

## Run Multiple Commands

A chain of commands can be run from a single line, separate each process with `/`.

```
equity/fundamental/balance --symbol MSFT --provider yfinance --period quarter --export msft_financials.xlsx --sheet-name balance/cash --symbol MSFT --provider yfinance --period quarter --export msft_financials.xlsx --sheet-name cash/income --symbol MSFT --provider yfinance --period quarter --export msft_financials.xlsx --sheet-name income
```

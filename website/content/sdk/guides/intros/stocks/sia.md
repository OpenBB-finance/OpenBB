---
title: Sector and Industry Analysis
keywords:
  [
    "sector, stock, industry, analysis, country, pie, chart, analyze",
  ]
excerpt: "This guide introduces the SIA SDK in the context of the OpenBB SDK."
---

The SIA module provides programmatic access to the commands from within the
OpenBB Terminal. Import the OpenBB SDK module, and then access the functions
similarly to how the Terminal menus are navigated. The code completion will be
activated upon entering `.`, after, `openbb.sia` ​

## How to Use

​ The examples provided below will assume that the following import block is
included at the beginning of the Python script or Notebook file: ​

```python
from openbb_terminal.sdk import openbb
```

​ A brief description below highlights the main Functions and Modules available
in the SIA SDK

| Path                     |   Type   |                                            Description |
| :----------------------- | :------: | -----------------------------------------------------: |
| openbb.stocks.sia.filter_stocks | Function |         generates a list of tickers filtered on inputs |
| openbb.stocks.sia.cpci          | Function | companies per Country based on Industry and Market Cap |
| openbb.stocks.sia.cpcs          | Function |   companies per Country based on Sector and Market Cap |
| openbb.stocks.sia.cpic          | Function | companies per Industry based on Country and Market Cap |
| openbb.stocks.sia.cpis          | Function |  companies per Industry based on Sector and Market Cap |
| openbb.stocks.sia.cps           | Function |   companies per Sector based on Country and Market Cap |
| openbb.stocks.sia.countries     | Function |                lists all countries valid for selection |
| openbb.stocks.sia.industries    | Function |               lists all industries valid for selection |
| openbb.stocks.sia.maketcap      | Function |               lists all marketcaps valid for selection |
| openbb.stocks.sia.sectors       | Function |                  lists all sectors valid for selection |
| openbb.stocks.sia.stocks_data   | Function |              historics financial statement information |

Alteratively you can print the contents of the SIA SDK with: ​

```python
help(openbb.stocks.sia)
```

## Examples

### cpci_chart

​ Creates a pie chart with information about the sector and market cap provided.
This allows you to better understand which countries the sector is centered in ​

```python
openbb.stocks.sia.cpci_chart()
```

​

![CPCI Chart](https://user-images.githubusercontent.com/72827203/202655235-eb4bf75e-852b-4128-8680-d99864358c73.png)

### industries

Creates a list of all industries that can be selected for other commands. Also
allows users to filter based on certain characteristics ​

```python
openbb.stocks.sia.industries(country="Germany", sector="Healthcare")
```

```python
['Biotechnology', 'Diagnostics & Research', 'Drug Manufacturers - General',
 'Drug Manufacturers - Major', 'Drug Manufacturers - Specialty & Generic', 'Drugs - Generic',
 'Health Information Services', 'Hospitals', 'Medical Care Facilities',
 'Medical Devices', 'Medical Distribution', 'Medical Instruments & Supplies']
```

### stocks_data

Creates a list of tickers filtered based on the given parameters ​

```python
openbb.stocks.sia.filter_stocks(country="Germany", industry="Auto Parts")
```

```python
['CTTAF', 'CTTAY', 'HLKHF', 'HLLGY', 'KNRRY', 'VOAXF']
```

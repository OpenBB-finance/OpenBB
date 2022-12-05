---
title: Government
---

The Government module provides programmatic access to the same functions from the [OpenBB Terminal](https://docs.openbb.co/terminal/guides/intros/stocks/gov). They provide an excellent supplement to fundamental and macroeconomic research. Please note that this module will only return data from the USA.

## How to Use

Below is a list of all the commands and a brief description. There are two types of function: ticker-specific, and non-specific. Many of these tables also have a companion `_chart` function.

|Path |Type| Description |
|:----------------|:------:|----------------------------:|
|openbb.stocks.gov.contracts|Ticker |Contracts Awarded to a Company |
|openbb.stocks.gov.gtrades |Ticker |Reported Trades in a Company's Stock by Members of the US Congress and Senate |
|openbb.stocks.gov.histcont|Ticker |The Quarterly Total Amount Paid to a Company by the Government |
|openbb.stocks.gov.lastcontracts |All |The Latest Invoices Paid by the US Treasury Department |
|openbb.stocks.gov.lasttrades| All|The Latest Reported Trades Made by Members of the US Congress and Senate |
|openbb.stocks.gov.lobbying|Ticker | Recorded Lobbying Efforts by a Company |
|openbb.stocks.gov.qtrcontracts|All |Ranking Companies by Total Amount Rewarded |
|openbb.stocks.gov.topbuys|All |The Top Buyers in Office |
|openbb.stocks.gov.toplobbying|All |Corporate Lobbyist Activity and the Specific Issues |
|openbb.stocks.gov.topsells|All |The Top Sellers in Office |

Alternatively, Python's built-in help will display the contents of the module, or specific function.

```python
help(openbb.stocks.gov)
```

## Examples

### Import Statements

The examples below will assume that this block is included at the top of the file:

```python
from openbb_terminal.sdk import openbb
```

### Toplobbying

This command shows who is spending money in Washington and what their intentions are.

```python
openbb.stocks.gov.toplobbying()
```

|    | Date       | Ticker   | Client                          |   Amount | Issue                | Specific_Issue  |
|---:|:-----------|:---------|:--------------------------------|---------:|:-------------------------------------|:--------------------|
| 495 | 2022-10-20 | DKNG     | DRAFTKINGS INC.                                   |    20000 | Taxation/Internal Revenue Code                | Tax characterization of daily fantasy sports.                               |
| 496 | 2022-10-20 | ELVT     | ELEVATE CREDIT SERVICE, LLC                       |    90000 | Banking                                       | Monitored issues concerning online lending proposals.                       |
| 497 | 2022-10-20 | HGV      | HILTON GRAND VACATIONS                            |    20000 | Financial Institutions/Investments/Securities | GENERAL DISCUSSIONS RELATED TO DEBT SERVICING                               |
| 498 | 2022-10-20 | SO       | SOUTHERN CALIFORNIA TRIBAL CHAIRMEN'S ASSOCIATION |    40000 | Indian/Native American Affairs                | Fee to trust issues. Issues surrounding federal programs for Indian tribes. |
| 499 | 2022-10-20 | ONCS     | ONCOSEC MEDICAL INCORPORATED                      |        0 |                                         |                                                                             |

### Contracts

Get a list of contracts awarded to a company and the agency authorizing it.

```python
openbb.stocks.gov.contracts('AMT')
```

|    | Date       | Description                                                                                                                                                                                     | Agency                                |   Amount |
|---:|:-----------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------|---------:|
|  0 | 2022-10-16 | RENTAL TOWER SITE                                                                                                                                                                               | DEPARTMENT OF JUSTICE (DOJ)           |     0    |
|  1 | 2022-10-01 | ANTENNA LEASE SITE 43  AMERICAN TOWER                                                                                                                                                           | DEPARTMENT OF HOMELAND SECURITY (DHS) | 13699.9  |
|  2 | 2022-10-01 | IGF::OT::IGF                                                                                                                                                                                    | DEPARTMENT OF JUSTICE (DOJ)           |  5100    |
|  3 | 2022-10-01 | LEASE OF RADIO REPEATER SITE                                                                                                                                                                    | DEPARTMENT OF THE TREASURY (TREAS)    |  9787.84 |
|  4 | 2022-10-01 | IGF::OT::IGF::-RECUR SERVICE FOR ANTENNA SITE  J ACCOUNT   LEASE AT:  MARIETTA, GA (BLACKWELL SITE)                                                                                             | DEPARTMENT OF JUSTICE (DOJ)           |     0    |
|  5 | 2022-10-01 | FUNDING FOR FY 2018 THROUGH FY 2019 ANTENNA SITE AGREEMENTS                                                                                                                                     | DEPARTMENT OF STATE (DOS)             | 30000    |

### Histcont

Get the historic (from 2008) quarterly sum paid to a company by the US Treasury department.

```python
openbb.stocks.gov.histcont('AMT')
```

|    |   Qtr |   Year |   Amount |
|---:|------:|-------:|---------:|
|  0 |     4 |   2021 |   127282 |
|  1 |     3 |   2021 |   564310 |
|  2 |     2 |   2021 |   564645 |
| 52 |     4 |   2008 |   110021 |
| 53 |     3 |   2008 |   240877 |
| 54 |     2 |   2008 |   907099 |
| 55 |     1 |   2008 |   320620 |

### Lobbying

Find the records of a company's lobbying efforts.

```python
openbb.stocks.gov.lobbying('AMT')
```

|    | Date       | Ticker   | Client                     |   Amount | Issue                                  | Specific_Issue                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|---:|:-----------|:---------|:---------------------------|---------:|:---------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  0 | 2022-12-01 | AMT      | AMERICAN TOWER CORPORATION |   440000 | Trade (domestic/foreign)               | Issues pertaining to global trade, global development, AID and the World Bank including trade policy with India - no specific legislation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|    |            |          |                            |          |  Communications/Broadcasting/Radio/TV  |  Telecommunication infrastructure issues including those related to the Federal Communications Commission - no specific legislation. Issues related to NTIA - including implementation of broadband funding programs in the Infrastructure Investment and Jobs Act, HR 3684. Issues related to 5G and wireless communications deployment - no specific legislation. Issues related to the definition of eligible project costs - no specific legislation. Issues pertaining to broadband deployment, including relevant provisions in the Infrastructure Investment and Jobs Act, HR 3684 and related legislation.  |
|    |            |          |                            |          |  Telecommunications                    |  Issues pertaining to telecommunications tower real estate - no specific legislation. Issues related to global telecommunications policy - no specific legislation.                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|    |            |          |                            |          |  Taxation/Internal Revenue Code        |  Issues related to international and domestic tax provisions as applied to real estate investment trusts and Public Law 115-97 (Tax Cuts and Jobs Act), including H.R. 5376, the Inflation Reduction Act of 2022. |

### Lastcontracts

Find out who is selling ink, toner cartridges, or other seemingly mundane items, to the Federal government.

```python
openbb.stocks.gov.lastcontracts()
```

|    | Date                | Ticker   |   Amount | Description                                       | Agency                                |
|---:|:--------------------|:---------|---------:|:--------------------------------------------------|:--------------------------------------|
|  0 | 2022-12-02 00:00:00 | DNOW     |    81.3  | CASE, FILING, TRANSFER: ITEM NAME CASE, FILING,   | GENERAL SERVICES ADMINISTRATION (GSA) |
|    |                     |          |          | TRANSFER INSIDE WIDTH 8.250 INCHES INSIDE LENGTH  |                                       |
|    |                     |          |          | 5.500 INCHES INSIDE DEPTH 10.75 INCHES CARD WIDTH |                                       |
|    |                     |          |          | 8.000 INCHES CARD LENGTH 5.000 INCHES CARD        |                                       |
|    |                     |          |          | CAPACITY 1,200 UNIT TYPE BOX UNIT DESIGN NON-     |                                       |
|    |                     |          |          | COLLAPSIBL                                        |                                       |
|  1 | 2022-12-02 00:00:00 | DNOW     |   855.6  | CARTRIDGE,TONER                                   | GENERAL SERVICES ADMINISTRATION (GSA) |
|  2 | 2022-12-02 00:00:00 | DNOW     |   169.84 | TONER,HP 508X HY, LJ,YL                           | GENERAL SERVICES ADMINISTRATION (GSA) |
|  3 | 2022-12-02 00:00:00 | DNOW     |   519.5  | CARTRIDGE,INK                                     | GENERAL SERVICES ADMINISTRATION (GSA) |
|  4 | 2022-12-02 00:00:00 | DNOW     |  1778.1  | OEM HP HY TONER, YELLOW, YLD 23K                  | GENERAL SERVICES ADMINISTRATION (GSA) |

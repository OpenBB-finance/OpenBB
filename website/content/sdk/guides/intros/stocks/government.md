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

Let's import the SDK in a way that reduces the amount of typing required to access the module.

### Import Statements

```python
from openbb_terminal.sdk import openbb
gov = openbb.stocks.gov
```

The examples below will assume that the block above is included at the top of the file.

### Toplobbying

This command shows who is spending money in Washington and what their intentions are.

```python
gov.toplobbying()
```

|    | Date       | Ticker   | Client                          |   Amount | Issue                | Specific_Issue  |
|---:|:-----------|:---------|:--------------------------------|---------:|:-------------------------------------|:--------------------|
|  0 | 2022-12-02 | ASTI     | ASCENT SOLAR TECHNOLOGIES, INC. |    10000 | Energy/Nuclear                         | Researching available funding, grants and loans for renewable energy.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
|  1 | 2022-12-02 | BUR      | BURFORD CAPITAL LLC             |   190000 | Torts                                  | - S.840/HR 2025 - Litigation Funding Transparency Act of 2021                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|  2 | 2022-12-01 | BLUE     | BLUEBIRD BIO                    |        0 |                                        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|  3 | 2022-12-01 | AMT      | AMERICAN TOWER CORPORATION      |   440000 | Trade (domestic/foreign)               | Issues pertaining to global trade, global development, AID and the World Bank including trade policy with India - no specific legislation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|    |            |          |                                 |          |  Communications/Broadcasting/Radio/TV  |  Telecommunication infrastructure issues including those related to the Federal Communications Commission - no specific legislation. Issues related to NTIA - including implementation of broadband funding programs in the Infrastructure Investment and Jobs Act, HR 3684. Issues related to 5G and wireless communications deployment - no specific legislation. Issues related to the definition of eligible project costs - no specific legislation. Issues pertaining to broadband deployment, including relevant provisions in the Infrastructure Investment and Jobs Act, HR 3684 and related legislation.  |
|    |            |          |                                 |          |  Telecommunications                    |  Issues pertaining to telecommunications tower real estate - no specific legislation. Issues related to global telecommunications policy - no specific legislation.                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|    |            |          |                                 |          |  Taxation/Internal Revenue Code        |  Issues related to international and domestic tax provisions as applied to real estate investment trusts and Public Law 115-97 (Tax Cuts and Jobs Act), including H.R. 5376, the Inflation Reduction Act of 2022.                                                                                                                                                                                                                                                                                                                                                                                                   |
|  4 | 2022-12-01 | AMT      | AMERICAN TOWER CORPORATION      |   360000 | Trade (domestic/foreign)               | Issues pertaining to global trade, global development, AID and the World Bank including trade policy with India - no specific legislation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|    |            |          |                                 |          |  Communications/Broadcasting/Radio/TV  |  Telecommunication infrastructure issues including those related to the Federal Communications Commission - no specific legislation. Issues related to NTIA - including implantation of Infrastructure Investment and Jobs Act, HR 3684, programs. Issues related to 5G and wireless communications deployment - no specific legislation. Issues related to the definition of eligible project costs - no specific legislation. Issues pertaining to broadband deployment, including relevant provisions in the Infrastructure Investment and Jobs Act, HR 3684 and related legislation.                            |
|    |            |          |                                 |          |  Telecommunications                    |  Issues pertaining to telecommunications tower real estate - no specific legislation. Issues related to global telecommunications policy - no specific legislation.                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|    |            |          |                                 |          |  Taxation/Internal Revenue Code        |  Issues related to international and domestic tax provisions as applied to real estate investment trusts and Public Law 115-97 (Tax Cuts and Jobs Act). |
| 495 | 2022-10-20 | DKNG     | DRAFTKINGS INC.                                   |    20000 | Taxation/Internal Revenue Code                | Tax characterization of daily fantasy sports.                               |
| 496 | 2022-10-20 | ELVT     | ELEVATE CREDIT SERVICE, LLC                       |    90000 | Banking                                       | Monitored issues concerning online lending proposals.                       |
| 497 | 2022-10-20 | HGV      | HILTON GRAND VACATIONS                            |    20000 | Financial Institutions/Investments/Securities | GENERAL DISCUSSIONS RELATED TO DEBT SERVICING                               |
| 498 | 2022-10-20 | SO       | SOUTHERN CALIFORNIA TRIBAL CHAIRMEN'S ASSOCIATION |    40000 | Indian/Native American Affairs                | Fee to trust issues. Issues surrounding federal programs for Indian tribes. |
| 499 | 2022-10-20 | ONCS     | ONCOSEC MEDICAL INCORPORATED                      |        0 |                                         |                                                                             |

### Contracts

Get a list of contracts awarded to a company and the agency authorizing it.

```python
gov.contracts('AMT')
```

|    | Date       | Description                                                                                                                                                                                     | Agency                                |   Amount |
|---:|:-----------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------|---------:|
|  0 | 2022-10-16 | RENTAL TOWER SITE                                                                                                                                                                               | DEPARTMENT OF JUSTICE (DOJ)           |     0    |
|  1 | 2022-10-01 | ANTENNA LEASE SITE 43  AMERICAN TOWER                                                                                                                                                           | DEPARTMENT OF HOMELAND SECURITY (DHS) | 13699.9  |
|  2 | 2022-10-01 | IGF::OT::IGF                                                                                                                                                                                    | DEPARTMENT OF JUSTICE (DOJ)           |  5100    |
|  3 | 2022-10-01 | LEASE OF RADIO REPEATER SITE                                                                                                                                                                    | DEPARTMENT OF THE TREASURY (TREAS)    |  9787.84 |
|  4 | 2022-10-01 | IGF::OT::IGF::-RECUR SERVICE FOR ANTENNA SITE  J ACCOUNT   LEASE AT:  MARIETTA, GA (BLACKWELL SITE)                                                                                             | DEPARTMENT OF JUSTICE (DOJ)           |     0    |
|  5 | 2022-10-01 | FUNDING FOR FY 2018 THROUGH FY 2019 ANTENNA SITE AGREEMENTS                                                                                                                                     | DEPARTMENT OF STATE (DOS)             | 30000    |
|  6 | 2022-10-01 | ANTENNA LEASE                                                                                                                                                                                   | DEPARTMENT OF THE TREASURY (TREAS)    | 32316    |
|  7 | 2022-10-01 | IGF::OT::IGF ANTENNA SITES                                                                                                                                                                      | DEPARTMENT OF HOMELAND SECURITY (DHS) | 41186.3  |
|  8 | 2022-10-01 | ANTENNA LEASE SITE #43 AMERICAN TOWER SITE NAME: YOUNGSTOWN S. 1443 AMERICAN TOWER SITE #: 307645                                                                                               | DEPARTMENT OF HOMELAND SECURITY (DHS) | 14110.9  |
|  9 | 2022-10-01 | PAIS: IGF::OT::IGF, SERVICE CONTRACT FOR RENTAL OF RADIO TOWER AT PORT MANSFIELD, TX TOWER SITE FOR RADIO COMMUNICATIONS. THIS CONTRACT IS FOR ONE BASE YEAR&4 OPTION YEARS THROUGH 12/31/2023. | DEPARTMENT OF THE INTERIOR (DOI)      | 38482.7  |
| 10 | 2022-10-01 | IGF::OT::IGF                                                                                                                                                                                    | DEPARTMENT OF JUSTICE (DOJ)           |     0    |
| 11 | 2022-10-01 | ANTENNA SITES 113 AND 143                                                                                                                                                                       | DEPARTMENT OF HOMELAND SECURITY (DHS) | 29099.6  |
| 12 | 2022-10-01 | IGF::OT::IGF BO/AMERICAN TOWERS ASSET SUB DBA SPECTRASITE COMMUNICATIONS/ANTENNA/WIR/11-01-18>10-31-19                                                                                          | DEPARTMENT OF JUSTICE (DOJ)           |  7692.24 |
| 13 | 2022-10-01 | TUCSON MOUNTAIN                                                                                                                                                                                 | DEPARTMENT OF THE TREASURY (TREAS)    | 10056.8  |
| 14 | 2022-09-10 | TOWER SITE RENTAL  REQUEST IS SUBJECT TO THE AVAILABILITY OF FY2023 FUNDS                                                                                                                       | DEPARTMENT OF JUSTICE (DOJ)           |     0    |
| 15 | 2022-05-21 | FISCAL YEAR 2021 ANTENNA SITE(S) #043, LEASE RENEWAL - SUBJECT TO AVAILABILITY OF FUNDS.                                                                                                        | DEPARTMENT OF HOMELAND SECURITY (DHS) |     0    |

### Histcont

Get the historic (from 2008) quarterly sum paid to a company by the US Treasury department.

```python
gov.histcont('AMT')
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
gov.lobbying('AMT', limit = 500)
```

|    | Date       | Ticker   | Client                     |   Amount | Issue                                  | Specific_Issue                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|---:|:-----------|:---------|:---------------------------|---------:|:---------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  0 | 2022-12-01 | AMT      | AMERICAN TOWER CORPORATION |   440000 | Trade (domestic/foreign)               | Issues pertaining to global trade, global development, AID and the World Bank including trade policy with India - no specific legislation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|    |            |          |                            |          |  Communications/Broadcasting/Radio/TV  |  Telecommunication infrastructure issues including those related to the Federal Communications Commission - no specific legislation. Issues related to NTIA - including implementation of broadband funding programs in the Infrastructure Investment and Jobs Act, HR 3684. Issues related to 5G and wireless communications deployment - no specific legislation. Issues related to the definition of eligible project costs - no specific legislation. Issues pertaining to broadband deployment, including relevant provisions in the Infrastructure Investment and Jobs Act, HR 3684 and related legislation.  |
|    |            |          |                            |          |  Telecommunications                    |  Issues pertaining to telecommunications tower real estate - no specific legislation. Issues related to global telecommunications policy - no specific legislation.                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|    |            |          |                            |          |  Taxation/Internal Revenue Code        |  Issues related to international and domestic tax provisions as applied to real estate investment trusts and Public Law 115-97 (Tax Cuts and Jobs Act), including H.R. 5376, the Inflation Reduction Act of 2022.                                                                                                                                                                                                                                                                                                                                                                                                   |
|  1 | 2022-12-01 | AMT      | AMERICAN TOWER CORPORATION |   360000 | Trade (domestic/foreign)               | Issues pertaining to global trade, global development, AID and the World Bank including trade policy with India - no specific legislation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|    |            |          |                            |          |  Communications/Broadcasting/Radio/TV  |  Telecommunication infrastructure issues including those related to the Federal Communications Commission - no specific legislation. Issues related to NTIA - including implantation of Infrastructure Investment and Jobs Act, HR 3684, programs. Issues related to 5G and wireless communications deployment - no specific legislation. Issues related to the definition of eligible project costs - no specific legislation. Issues pertaining to broadband deployment, including relevant provisions in the Infrastructure Investment and Jobs Act, HR 3684 and related legislation.                            |
|    |            |          |                            |          |  Telecommunications                    |  Issues pertaining to telecommunications tower real estate - no specific legislation. Issues related to global telecommunications policy - no specific legislation.                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|    |            |          |                            |          |  Taxation/Internal Revenue Code        |  Issues related to international and domestic tax provisions as applied to real estate investment trusts and Public Law 115-97 (Tax Cuts and Jobs Act).                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|  2 | 2022-10-20 | AMT      | AMERICAN TOWER CORPORATION |    50000 | Taxation/Internal Revenue Code         | Taxation issues related to Real Estate Investment Trusts (REITs).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|  3 | 2022-10-20 | AMT      | AMERICAN TOWER CORPORATION |    18000 | Trade (domestic/foreign)               | Issues pertaining to global trade, global development, AID and the World Bank (no specific legislation).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|    |            |          |                            |          |  Communications/Broadcasting/Radio/TV  |  Issues related to the Federal Communications Commission (no specific legislation); Issues related to NTIA (no specific legislation); Issues pertaining to rural broadband development (no specific legislation); Issues related to 5G and broadband deployment (no specific legislation); H.R.5376 (Build Back Better Act) - provisions affecting broadband and mobile telecommunications; H.R.3684 (Infrastructure Investment and Jobs Act) - provisions affecting broadband and mobile telecommunications.                                                                                                       |
|    |            |          |                            |          |  Taxation/Internal Revenue Code        |  Issues related to international and domestic tax provisions as applied to real estate investment trusts; H.R.5376 (Build Back Better Act) - provisions affecting broadband and mobile telecommunications; H.R.3684 (Infrastructure Investment and Jobs Act) - provisions affecting broadband and mobile telecommunications.                                                                                                                                                                                                                                                                                        |
|    |            |          |                            |          |  Telecommunications                    |  American Jobs Plan Proposal and Bi-Partisan Infrastructure Framework regarding matters pertaining to cellular and broadband infrastructure and 5G development and deployment; Issues pertaining to telecommunications tower real estate; H.R.1319 (American Rescue Act of 2021) - state and local assistance; H.R.5376 (Build Back Better Act) - provisions affecting broadband and mobile telecommunications; H.R.3684 (Infrastructure Investment and Jobs Act) - provisions affecting broadband and mobile telecommunications.                                                                                   |
|  4 | 2022-10-20 | AMT      | AMERICAN TOWER CORPORATION |   410000 | Trade (domestic/foreign)               | Issues pertaining to global trade, global development, AID and the World Bank including trade policy with India - no specific legislation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|    |            |          |                            |          |  Communications/Broadcasting/Radio/TV  |  Telecommunication infrastructure issues including those related to the Federal Communications Commission - no specific legislation. Issues related to NTIA - including implementation of broadband funding programs in the Infrastructure Investment and Jobs Act, HR 3684. Issues related to 5G and wireless communications deployment - no specific legislation. Issues related to the definition of eligible project costs - no specific legislation. Issues pertaining to broadband deployment, including relevant provisions in the Infrastructure Investment and Jobs Act, HR 3684 and related legislation.  |
|    |            |          |                            |          |  Telecommunications                    |  Issues pertaining to telecommunications tower real estate - no specific legislation. Issues related to global telecommunications policy - no specific legislation.                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|    |            |          |                            |          |  Taxation/Internal Revenue Code        |  Issues related to international and domestic tax provisions as applied to real estate investment trusts and Public Law 115-97 (Tax Cuts and Jobs Act), including H.R. 5376, the Inflation Reduction Act of 2022.  |
| 170 | 2009-07-13 | AMT      | AMERICAN TOWER CORPORATION |        0 |                    |                                                                                                      |
| 171 | 2009-04-15 | AMT      | AMERICAN TOWER CORPORATION |    10000 | Telecommunications | Rural broadband deployment provisions in H.R. 1, the American Recovery and Reinvestment Act of 2009. |
| 172 | 2009-02-12 | AMT      | AMERICAN TOWER CORPORATION |        0 | Telecommunications | Broadband access incentive provisions in H.R. 1, The American Recovery and Reinvestment Act of 2009. |
| 173 | 2004-02-20 | AMT      | AMERICAN TOWER CORP        |        0 | Telecommunications |                                                                                                      |
| 174 | 2004-02-20 | AMT      | AMERICAN TOWER CORP        |    20000 | Telecommunications |                                                                                                      |

### Lastcontracts

Find out who is selling ink, toner cartridges, or other seemingly mundane items, to the Federal government.

```python
gov.lastcontracts()
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

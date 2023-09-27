---
title: Insiders
keywords: [stocks, insiders, transactions, form-4, sec, ceo, cfo, major holder, director, sale, award, grant, option]
description: This guide introduces the Stocks Insiders module by briefly explaining the functions and how to use them.
---
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

`<HeadTitle title="Stocks Insiders - SDK | OpenBB Docs" />`

## Overview

The Insiders module provides endpoints to the [Insiders Trading menu in the OpenBB Terminal](https://docs.openbb.co/terminal/usage/intros/stocks/ins).  The contents of the module are displayed on screen with:

```python
openbb.stocks.ins?
```

or:

```python
help(openbb.stocks.ins)
```

```python
Type:        property
String form: <property object at 0x7f3df1102f70>
Docstring:  
Stocks Insiders Submodule

Attributes:

    `act`: Get insider activity. [Source: Business Insider]

    `act_chart`: Display insider activity. [Source: Business Insider]

    `blcp`: Get latest CEO/CFO purchases > 25k

    `blcs`: Get latest CEO/CFO sales > 100k

    `blip`: Get latest insider purchases > 25k

    `blis`: Get latest insider sales > 100k

    `blop`: Get latest officer purchases > 25k

    `blos`: Get latest officer sales > 100k

    `filter`: Get insider trades based on preset filter

    `lcb`: Get latest cluster buys

    `lins`: Get last insider activity for a given stock ticker. [Source: Finviz]

    `lins_chart`: Display insider activity for a given stock ticker. [Source: Finviz]

    `lip`: Get latest insider purchases

    `lis`: Get latest insider sales

    `lit`: Get latest insider trades

    `lpsb`: Get latest penny stock buys

    `print_insider_data`: Print insider data

    `print_insider_data_chart`: Print insider data

    `stats`: Get OpenInsider stats for ticker
```

## How to Use

Try the next two commands for ticker-specific information.

### stats

The last 100 results are returned.

```python
openbb.stocks.ins.stats('wmt')
```

|   | X | Filing Date         | Trading Date | Ticker | Insider         | Title    | Trade Type | Price                                                              | Quantity                                                                              | Owned                      | Delta Own                                              | Value | Filing Link | Ticker Link | Insider Link |
| -: | :- | :------------------ | :----------- | :----- | :-------------- | :------- | :--------- | :----------------------------------------------------------------- | :------------------------------------------------------------------------------------ | :------------------------- | :----------------------------------------------------- | :---- | :---------- | :---------- | :----------- |
| 0 |   | 2023-05-01 17:18:33 | 2023-04-27   | WMT    | Furner John R.  | EVP      | S - Sale   | $151.00 | -4,375     | 288,434       | -1%         | -$660,625     | http://www.sec.gov/Archives/edgar/data/104169/000112760223013917/xslF345X03/form4.xml | http://openinsider.com/WMT | http://openinsider.com/insider/Furner-John-R./1696737  |       |             |             |              |
| 1 | M | 2023-03-30 18:36:05 | 2023-03-29   | WMT    | Walton S Robson | Dir, 10% | S - Sale   | $144.75 | -3,412,370 | 1,249,821,970 | 0%          | -$493,930,674 | http://www.sec.gov/Archives/edgar/data/104169/000112760223011663/xslF345X03/form4.xml | http://openinsider.com/WMT | http://openinsider.com/insider/Walton-S-Robson/1219112 |       |             |             |              |

### act

This command returns the information a bit differently.

```python
openbb.stocks.ins.act('wmt')
```

| Date                | Shares Traded | Shares Held    |  Price | Type | Option | Insider         |
| :------------------ | :------------ | :------------- | -----: | :--- | :----- | :-------------- |
| 2023-03-27 00:00:00 | 341,149.00    | 249,123,886.00 | 144.23 | Sell | No     | WALTON S ROBSON |
| 2023-03-27 00:00:00 | 341,149.00    | 249,123,886.00 | 144.23 | Sell | No     | WALTON ALICE L  |
| 2023-03-27 00:00:00 | 1,259,851.00  | 249,465,035.00 | 143.71 | Sell | No     | WALTON ALICE L  |
| 2023-03-28 00:00:00 | 1,640,457.00  | 247,483,429.00 | 144.06 | Sell | No     | WALTON S ROBSON |
| 2023-03-28 00:00:00 | 267,874.00    | 247,215,555.00 |  144.7 | Sell | No     | WALTON S ROBSON |
| 2023-03-28 00:00:00 | 1,640,457.00  | 247,483,429.00 | 144.06 | Sell | No     | WALTON ALICE L  |

Other functions in this module return all tickers, based on the latest SEC Form-4 filings.

### lpsb

Short for, Latest Penny Stock Buys, this command filters for insider purchases of penny stocks.

```python
openbb.stocks.ins.lpsb().head(3)
```

|   | X | Filing Date | Trade Date | Ticker | Company Name         | Insider Name        | Title     | Trade Type   | Price                                               | Qty | Owned | Diff Own | Value |
| -: | :- | :---------- | :--------- | :----- | :------------------- | :------------------ | :-------- | :----------- | :-------------------------------------------------- | --: | ----: | :------- | :---- |
| 0 | M | 2023-05-17  | 2023-05-15 | ADV    | Advantage Solutions  | Peacock David A     | CEO       | P - Purchase | $1.61   | 160000 | 1858112 | +9%        | +$257,752 |     |       |          |       |
|   |   | 16:30:22    |            |        | Inc.                 |                     |           |              |                                                     |     |       |          |       |
| 1 | - | 2023-05-17  | 2023-05-17 | SOND   | Sonder Holdings Inc. | Rothenberg Philip L | GC,       | P - Purchase | $0.45   | 300000 |  300000 | New        | +$135,000 |     |       |          |       |
|   |   | 16:17:31    |            |        |                      |                     | Secretary |              |                                                     |     |       |          |       |
| 2 | M | 2023-05-17  | 2023-05-15 | SOND   | Sonder Holdings Inc. | Davidson Francis    | CEO       | P - Purchase | $0.41   | 615645 | 4060224 | +18%       | +$249,596 |     |       |          |       |
|   |   | 16:15:08    |            |        |                      |                     |           |              |                                                     |     |       |          |       |

### lit

Stands for, Latest Insider Trades, and returns the last one-hundred insider trades, market-wide.

```python
openbb.stocks.ins.lit().head(3)
```

|   | X  | Filing Date | Trade Date | Ticker | Company Name         | Insider Name     | Title      | Trade Type  | Price                                                  | Qty | Owned | Diff Own | Value |
| -: | :- | :---------- | :--------- | :----- | :------------------- | :--------------- | :--------- | :---------- | :----------------------------------------------------- | --: | ----: | :------- | :---- |
| 0 | DM | 2023-05-17  | 2023-05-15 | AMZN   | Amazon Com Inc       | Selipsky Adam    | CEO Amazon | S - Sale+OE | $110.47 |  -11260 |  150103 | -7%        | -$1,243,914 |     |       |          |       |
|   |    | 16:40:35    |            |        |                      |                  | Web        |             |                                                        |     |       |          |       |
|   |    |             |            |        |                      |                  | Services   |             |                                                        |     |       |          |       |
| 1 | D  | 2023-05-17  | 2023-05-15 | TDUP   | Thredup Inc.         | Nakache Patricia | Dir, 10%   | S - Sale+OE | $3.01   |  -28123 |   76976 | -27%       | -$84,650    |     |       |          |       |
|   |    | 16:39:59    |            |        |                      |                  |            |             |                                                        |     |       |          |       |
| 2 | -  | 2023-05-17  | 2023-05-15 | RRC    | Range Resources Corp | Scucchi Mark     | EVP, CFO   | S - Sale    | $27.39  | -153000 |  772540 | -17%       | -$4,190,670 |     |       |          |       |
|   |    | 16:39:52    |            |        |                      |                  |            |             |                                                        |     |       |          |       |

`lip` & `lis` filter for purchases and sales, respectively.

### filter

The `filter` function is a customizable screener that allows scanning in greater detail.  User-generated presets are saved in the OpenBBUserData folder, under:  `~/OpenBBUserData/presets/stocks/insider`.  Presets included with the code are located in the source code, [here](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/miscellaneous/stocks/insider).  Use, [template.ini](https://github.com/OpenBB-finance/OpenBBTerminal/blob/main/openbb_terminal/miscellaneous/stocks/insider/template.ini), as a starting point.  The following fields are allowed:

```console
[General]
# Symbols or CIKs
Tickers =
# Insider Name or CIK
Insider =
SharePriceMin =
SharePriceMax =
LiquidityMinM =
LiquidityMaxM =

[Date]
# All dates, Custom, Latest Day, Last 3 days, Last 1 week, Last 2 weeks, Last 1 month, Last 2 months, Last 3 months, Last 6 months, Last 1 year, Last 2 years, Last 4 years.
FilingDate = All dates
# This is only regarded if FillingDate = Custom, format: dd/mm/yyyy
FilingDateFrom =
FilingDateTo =
# All dates, Custom, Latest Day, Last 3 days, Last 1 week, Last 2 weeks, Last 1 month, Last 2 months, Last 3 months, Last 6 months, Last 1 year, Last 2 years, Last 4 years.
TradingDate = All dates
# This is only regarded if FillingDate = Custom, format: dd/mm/yyyy
TradingDateFrom =
TradingDateTo =
# These values need to be smaller than 100
FilingDelayMin =
FilingDelayMax =
NDaysAgo =

[TransactionFiling]
# The following values are meant to be either: 'true' or empty for False.
P_Purchase = true
S_Sale = true
A_Grant =
D_SaleToLoss =
G_Gift =
NoDeriv =
F_Tax =
M_OptionEx =
X_OptionEx =
C_CnvDeriv =
W_Inherited =
MultipleDays =
# These values need to be multiples of 5
TradedMinK =
TradedMaxK =
# These values need to be between 0 and 100%
OwnChangeMinPct =
OwnChangeMaxPct =

[Industry]
# Available industry options at bottom of the file.
# Sector -> Subsector -> Industry
SectorSubsectorIndustry = All Sectors (except Funds)

[InsiderTitle]
# The following values are meant to be either: 'true' or empty for False.
COB =
CEO =
Pres =
COO =
CFO =
GC =
VP =
# 'Officer' includes all of the above: COB, CEO, Pres, COO, CFO, GC, VP
Officer =
Director =
10PctOwn =
Other =

[Others]
# Filing, Company.
GroupBy = Filing
# Filing Date, Trade Date, Ticker Symbol, Trade Value.
SortBy = Filing Date
# 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000.
MaxResults = 100
# Between 1 and 99, inclusive.
Page = 1

# This only exists if GroupBy = Company
[CompanyTotals]
# These values need to be smaller than 100
FilingsMin =
FilingsMax =
# These values need to be smaller than 10
InsidersMin =
InsidersMax =
OfficersMin =
OfficersMax =
# These values need to be multiples of 5
TradedMinK =
TradedMaxK =
# These values need to be between 0 and 100%
OwnChangeMinPct =
OwnChangeMaxPct =
```

The sector industrial classification is also selectable.  Most of the included presets are for filtering by industry.  For example, `Mortgages`.  

**Do not include `.ini` in the preset name.**

```python
openbb.stocks.ins.filter("Mortgages")
```

|   | X | Filing Date         | Trading Date | Ticker | Insider                                                  | Title    | Trade Type   | Price                                                           | Quantity                                                                               | Owned                       | Delta Own                                                                                       | Value                             | Filing Link | Ticker Link | Insider Link | Company |
| -: | :- | :------------------ | :----------- | :----- | :------------------------------------------------------- | :------- | :----------- | :-------------------------------------------------------------- | :------------------------------------------------------------------------------------- | :-------------------------- | :---------------------------------------------------------------------------------------------- | :-------------------------------- | :---------- | :---------- | :----------- | :------ |
| 0 |   | 2023-04-05 18:25:23 | 2023-04-04   | PFSI   | Spector David                                            | COB, CEO | S - Sale     | $59.71  | -15,000     | 1,070,787  | -1%         | -$895,713    | http://www.sec.gov/Archives/edgar/data/1745916/000112760223012621/xslF345X03/form4.xml | http://openinsider.com/PFSI | http://openinsider.com/insider/Spector-David/1275713                                            | Pennymac Financial Services, Inc. |             |             |              |         |
| 1 | D | 2023-04-04 17:32:57 | 2023-03-31   | FOA    | Blackstone Tactical Opportunities Associates - Nq L.L.C. | 10%      | P - Purchase | $1.38   | +10,869,566 | 24,386,710 | +80%        | +$15,000,001 | http://www.sec.gov/Archives/edgar/data/1828937/000089924323010452/xslF345X03/doc4.xml  | http://openinsider.com/FOA  | http://openinsider.com/insider/Blackstone-Tactical-Opportunities-Associates---Nq-L.L.C./1844883 | Finance of America Companies Inc. |             |             |              |         |
| 2 | D | 2023-04-04 17:31:43 | 2023-03-31   | FOA    | Bto Urban Holdings L.L.C.                                | 10%      | P - Purchase | $1.38   | +10,869,566 | 24,386,710 | +80%        | +$15,000,001 | http://www.sec.gov/Archives/edgar/data/1828937/000089924323010448/xslF345X03/doc4.xml  | http://openinsider.com/FOA  | http://openinsider.com/insider/Bto-Urban-Holdings-L.L.C./1854686                                | Finance of America Companies Inc. |             |             |              |         |
| 3 | D | 2023-04-04 17:27:24 | 2023-03-31   | FOA    | Blackstone Tactical Opportunities Fund - U - Nq L.L.C.   | 10%      | P - Purchase | $1.38   | +10,869,566 | 24,386,710 | +80%        | +$15,000,001 | http://www.sec.gov/Archives/edgar/data/1828937/000089924323010444/xslF345X03/doc4.xml  | http://openinsider.com/FOA  | http://openinsider.com/insider/Blackstone-Tactical-Opportunities-Fund---U---Nq-L.L.C./1853348   | Finance of America Companies Inc. |             |             |              |         |

Try the  `whales`  preset to track some of the big money:

```python
openbb.stocks.ins.filter("whales")
```

|   | X  | Filing Date         | Trading Date | Ticker | Insider                   | Title                     | Trade Type   | Price                                                            | Quantity                                                                               | Owned                      | Delta Own                                                        | Value                          | Filing Link | Ticker Link | Insider Link | Company |
| -: | :- | :------------------ | :----------- | :----- | :------------------------ | :------------------------ | :----------- | :--------------------------------------------------------------- | :------------------------------------------------------------------------------------- | :------------------------- | :--------------------------------------------------------------- | :----------------------------- | :---------- | :---------- | :----------- | :------ |
| 0 | DM | 2023-05-15 21:26:39 | 2023-05-11   | OXY    | Berkshire Hathaway Inc    | 10%                       | P - Purchase | $58.06  | +2,165,792 | 213,966,443 | +1%         | +$125,746,876 | http://www.sec.gov/Archives/edgar/data/797468/000089924323013028/xslF345X03/doc4.xml   | http://openinsider.com/OXY | http://openinsider.com/insider/Berkshire-Hathaway-Inc/1067983    | Occidental Petroleum Corp /De/ |             |             |              |         |
| 1 | M  | 2023-05-15 16:32:03 | 2023-05-11   | MA     | Mastercard Foundation     | 10%                       | S - Sale     | $381.83 | -377,448   | 99,808,197  | 0%          | -$144,121,385 | http://www.sec.gov/Archives/edgar/data/1141391/000089534523000297/xslF345X03/form4.xml | http://openinsider.com/MA  | http://openinsider.com/insider/Mastercard-Foundation/1421897     | Mastercard Inc                 |             |             |              |         |
| 2 |    | 2023-05-12 19:50:56 | 2023-05-10   | STZ    | Ajb Business Holdings LP  | Member of 10% owner group | S - Sale     | $223.53 | -650,000   | 3,365,715   | -16%        | -$145,294,500 | http://www.sec.gov/Archives/edgar/data/16918/000089924323012892/xslF345X03/doc4.xml    | http://openinsider.com/STZ | http://openinsider.com/insider/Ajb-Business-Holdings-LP/1955386  | Constellation Brands, Inc.     |             |             |              |         |
| 3 |    | 2023-05-12 19:46:15 | 2023-05-10   | STZ    | Zmss Business Holdings LP | Member of 10% owner group | S - Sale     | $223.53 | -650,000   | 3,365,715   | -16%        | -$145,294,500 | http://www.sec.gov/Archives/edgar/data/16918/000089924323012888/xslF345X03/doc4.xml    | http://openinsider.com/STZ | http://openinsider.com/insider/Zmss-Business-Holdings-LP/1955193 | Constellation Brands, Inc.     |             |             |              |         |

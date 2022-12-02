---
title: Government
keywords:
  [
    "Government",
    "house",
    "senate",
    "politician",
    "lobby",
    "lobbyist",
    "contract",
    "contractor",
    "spending",
    "budget",
    "treasury",
    "trading",
    "buys",
    "sells",
    "ticker",
    "tickers",
    "companies",
    "listing",
    "exchange",
  ]
date: "2022-06-02"
type: guides
status: publish
excerpt: "This guide introduces the Government submenu, within the Stocks menu, by briefly explaining the features and how to use them, showing examples in context."
geekdocCollapseSection: true
---

The features in this menu are intended to show the reported trades of elected officials, lobbyist activity, awarded contracts, and general spending of the United States Treasury Department. This menu only covers the USA, or companies that trade on US exchanges. The information in this menu is compiled by <a href="https://www.quiverquant.com/" target="_blank" rel="noreferrer noopener">QuiverQuant</a>. A ticker is not required to enter the menu; navigate there from anywhere in the terminal with absolute path jumping: `/stocks/gov`

![The Government Menu](https://user-images.githubusercontent.com/85772166/173205843-1d9d5679-df73-4ec3-8b98-937f38ccac35.png)

### How to use

The menu is divided into two sections. Features under the `Explore` do not depend on individual tickers, while the commands listed under `Ticker` do. Entering `lasttrades -p 1` will return a table with the latest reported trades made by Congress members. The `-p 1` indicates it looks one day back.

```
(🦋) /stocks/gov/ $ lasttrades -p 1

Last transactions for CONGRESS

                                           Representative Trading
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Transaction Date ┃ Ticker ┃ Representative ┃ Transaction ┃ Range          ┃ House           ┃ Report Date ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 2022-11-14       │ RTX    │ Dwight Evans   │ Sale        │ $1,001-$15,000 │ Representatives │ 2022-11-21  │
├──────────────────┼────────┼────────────────┼─────────────┼────────────────┼─────────────────┼─────────────┤
│ 2022-11-14       │ BTEC   │ Dwight Evans   │ Sale        │ $1,001-$15,000 │ Representatives │ 2022-11-21  │
├──────────────────┼────────┼────────────────┼─────────────┼────────────────┼─────────────────┼─────────────┤
│ 2022-11-14       │ QYLD   │ Dwight Evans   │ Sale        │ $1,001-$15,000 │ Representatives │ 2022-11-21  │
├──────────────────┼────────┼────────────────┼─────────────┼────────────────┼─────────────────┼─────────────┤
│ 2022-11-14       │ RHHBY  │ Dwight Evans   │ Purchase    │ $1,001-$15,000 │ Representatives │ 2022-11-21  │
├──────────────────┼────────┼────────────────┼─────────────┼────────────────┼─────────────────┼─────────────┤
│ 2022-11-14       │ SRVR   │ Dwight Evans   │ Sale        │ $1,001-$15,000 │ Representatives │ 2022-11-21  │
├──────────────────┼────────┼────────────────┼─────────────┼────────────────┼─────────────────┼─────────────┤
│ 2022-11-14       │ SRE    │ Dwight Evans   │ Purchase    │ $1,001-$15,000 │ Representatives │ 2022-11-21  │
└──────────────────┴────────┴────────────────┴─────────────┴────────────────┴─────────────────┴─────────────┘
```

With `lasttrades senate -p 3` & `lasttrades house -p 3` it will select other elected officials.

```
(🦋) /stocks/gov/ $ lasttrades senate -p 3

Last transactions for SENATE

                              Representative Trading
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ Transaction Date ┃ Ticker ┃ Representative    ┃ Transaction ┃ Range             ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ 2022-10-31       │ CLF    │ Tuberville, Tommy │ Purchase    │ $15,001 - $50,000 │
├──────────────────┼────────┼───────────────────┼─────────────┼───────────────────┤
│ 2022-10-28       │ MSFT   │ Tuberville, Tommy │ Sale        │ $1,001 - $15,000  │
├──────────────────┼────────┼───────────────────┼─────────────┼───────────────────┤
│ 2022-10-28       │ MSFT   │ Tuberville, Tommy │ Sale        │ $1,001 - $15,000  │
├──────────────────┼────────┼───────────────────┼─────────────┼───────────────────┤
│ 2022-10-28       │ MSFT   │ Tuberville, Tommy │ Sale        │ $1,001 - $15,000  │
├──────────────────┼────────┼───────────────────┼─────────────┼───────────────────┤
│ 2022-10-25       │ FDX    │ Tuberville, Tommy │ Sale        │ $1,001 - $15,000  │
├──────────────────┼────────┼───────────────────┼─────────────┼───────────────────┤
│ 2022-10-25       │ FTBFX  │ Tuberville, Tommy │ Sale        │ $15,001 - $50,000 │
└──────────────────┴────────┴───────────────────┴─────────────┴───────────────────┘
(🦋) /stocks/gov/ $ lasttrades house -p 3

Last transactions for HOUSE

                              Representative Trading
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Transaction Date ┃ Ticker ┃ Representative      ┃ Transaction ┃ Range          ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ 2022-11-14       │ SRVR   │  Dwight Evans       │ Sale        │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-14       │ SRE    │  Dwight Evans       │ Purchase    │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-14       │ BTEC   │  Dwight Evans       │ Sale        │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-14       │ RHHBY  │  Dwight Evans       │ Purchase    │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-14       │ RTX    │  Dwight Evans       │ Sale        │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-14       │ QYLD   │  Dwight Evans       │ Sale        │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-09       │ PYPL   │  Cindy Axne         │ Sale        │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-09       │ ADBE   │  William R. Keating │ Sale        │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-09       │ PLD    │  Lois Frankel       │ Purchase    │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-09       │ PYPL   │  Cindy Axne         │ Sale        │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-09       │ NOW    │  William R. Keating │ Purchase    │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-09       │ PYPL   │  Cindy Axne         │ Sale        │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-03       │ ECL    │  Alan S. Lowenthal  │ Sale        │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-03       │ LMT    │  Cindy Axne         │ Sale        │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-03       │ TMUS   │  Alan S. Lowenthal  │ Sale        │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-03       │ ECL    │  Alan S. Lowenthal  │ Sale        │ $1,001-$15,000 │
├──────────────────┼────────┼─────────────────────┼─────────────┼────────────────┤
│ 2022-11-03       │ TMUS   │  Alan S. Lowenthal  │ Sale        │ $1,001-$15,000 │
└──────────────────┴────────┴─────────────────────┴─────────────┴────────────────┘
```

The `toplobbying` command brings up a bar graph of recent big spenders on K Street, that are listed on-exchange. The optional arguments `l`, `--raw` & `--export` changes the number of companies returned, shows a table of the raw data, or exports the data to a file.

![Top ten companies actively lobbying the US government](https://user-images.githubusercontent.com/85772166/173206158-bd42523c-50de-4f44-b1b5-7012cadc44a2.png)

The spending by government can be tracked with the command, `lastcontracts`.

```
(🦋) /stocks/gov/ $ lastcontracts -l 5

                                                      Last Government Contracts
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Date                ┃ Ticker ┃ Amount  ┃ Description                                      ┃ Agency                                ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2022-11-20 00:00:00 │ DNOW   │ 335.14  │ TONER,HP87X,HYIELD,LJ,BK                         │ GENERAL SERVICES ADMINISTRATION (GSA) │
├─────────────────────┼────────┼─────────┼──────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-11-20 00:00:00 │ DNOW   │ 6.18    │ KNIFE,CRAFTSMAN' S STANLEY MECHANICS P/N: 10-099 │ GENERAL SERVICES ADMINISTRATION (GSA) │
├─────────────────────┼────────┼─────────┼──────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-11-20 00:00:00 │ DNOW   │ 90.15   │ COUNTRY OF MANUFACTURE IS US                     │ GENERAL SERVICES ADMINISTRATION (GSA) │
├─────────────────────┼────────┼─────────┼──────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-11-20 00:00:00 │ DNOW   │ 21.84   │ BATTERIES                                        │ GENERAL SERVICES ADMINISTRATION (GSA) │
├─────────────────────┼────────┼─────────┼──────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-11-20 00:00:00 │ DNOW   │ 3698.92 │ ENVELOPES                                        │ GENERAL SERVICES ADMINISTRATION (GSA) │
└─────────────────────┴────────┴─────────┴──────────────────────────────────────────────────┴───────────────────────────────────────┘
```

### Examples

The command `gtrades` shows the trade movements based on a stock defined with `load`. For example, the following shows the governmental trades regarding Microsoft which can be shown with.

```
(🦋) /stocks/gov/ $ load MSFT

Loading Daily MSFT stock with starting period 2021-11-15 for analysis.

Company:  Microsoft Corporation
Exchange: NASDAQ/NMS (GLOBAL MARKET)
Currency: USD

(🦋) /stocks/gov/ $ gtrades
```

![Microsoft trades by elected officials](https://user-images.githubusercontent.com/85772166/173206175-e6b0436a-82cd-4075-b4bf-87926db0a31e.png)

A table of this chart, with representatives' names, is called by adding the `--raw` flag to the command string. For example for Apple.

```
(🦋) /stocks/gov/ $ load AAPL

Loading Daily AAPL stock with starting period 2019-11-18 for analysis.
g
Company:  Apple Inc.
Exchange: NASDAQ/NMS (GLOBAL MARKET)
Currency: USD

(🦋) /stocks/gov/ $ gtrades --raw

                                                                    Government Trading for AAPL
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ ReportDate ┃ TransactionDate     ┃ Ticker ┃ Representative       ┃ Transaction ┃ Amount   ┃ House           ┃ Range            ┃ min   ┃ max   ┃ lower  ┃ upper ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ 2022-07-22 │ 2022-06-14 00:00:00 │ AAPL   │  Josh Gottheimer     │ Sale        │ 1001.00  │ Representatives │ $1,001-$15,000   │ 1001  │ 15000 │ -15000 │ -1001 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-08-10 │ 2022-07-15 00:00:00 │ AAPL   │  Kathy Manning       │ Purchase    │ 15001.00 │ Representatives │ $15,001-$50,000  │ 15001 │ 50000 │ 15001  │ 50000 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-08-29 │ 2022-07-15 00:00:00 │ AAPL   │  Josh Gottheimer     │ Purchase    │ 1001.00  │ Representatives │ $1,001-$15,000   │ 1001  │ 15000 │ 1001   │ 15000 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-08-10 │ 2022-07-27 00:00:00 │ AAPL   │  Kathy Manning       │ Sale        │ 1001.00  │ Representatives │ $1,001-$15,000   │ 1001  │ 15000 │ -15000 │ -1001 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-08-10 │ 2022-07-27 00:00:00 │ AAPL   │  Kathy Manning       │ Sale        │ 1001.00  │ Representatives │ $1,001-$15,000   │ 1001  │ 15000 │ -15000 │ -1001 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-08-10 │ 2022-07-27 00:00:00 │ AAPL   │  Kathy Manning       │ Purchase    │ 1001.00  │ Representatives │ $1,001-$15,000   │ 1001  │ 15000 │ 1001   │ 15000 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-09-14 │ 2022-08-05 00:00:00 │ AAPL   │  Kathy Manning       │ Purchase    │ 1001.00  │ Representatives │ $1,001-$15,000   │ 1001  │ 15000 │ 1001   │ 15000 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-09-16 │ 2022-08-26 00:00:00 │ AAPL   │  Josh Gottheimer     │ Sale        │ 1001.00  │ Representatives │ $1,001-$15,000   │ 1001  │ 15000 │ -15000 │ -1001 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-09-23 │ 2022-08-26 00:00:00 │ AAPL   │  Robert B. Aderholt  │ Purchase    │ 1001.00  │ Representatives │ $1,001-$15,000   │ 1001  │ 15000 │ 1001   │ 15000 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-09-06 │ 2022-09-06 00:00:00 │ AAPL   │  Bob Gibbs           │ Purchase    │ 1001.00  │ Representatives │ $1,001-$15,000   │ 1001  │ 15000 │ 1001   │ 15000 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-09-06 │ 2022-09-06 00:00:00 │ AAPL   │  Bob Gibbs           │ Purchase    │ 1001.00  │ Representatives │ $1,001-$15,000   │ 1001  │ 15000 │ 1001   │ 15000 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-11-10 │ 2022-10-12 00:00:00 │ AAPL   │  Kathy Manning       │ Sale        │ 1001.00  │ Representatives │ $1,001-$15,000   │ 1001  │ 15000 │ -15000 │ -1001 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-11-13 │ 2022-10-17 00:00:00 │ AAPL   │ Shelley Moore Capito │ Sale        │ 1001.00  │ Senate          │ $1,001 - $15,000 │ 1001  │ 15000 │ -15000 │ -1001 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-11-10 │ 2022-10-19 00:00:00 │ AAPL   │  Josh Gottheimer     │ Purchase    │ 1001.00  │ Representatives │ $1,001-$15,000   │ 1001  │ 15000 │ 1001   │ 15000 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-11-10 │ 2022-10-25 00:00:00 │ AAPL   │  Josh Gottheimer     │ Sale        │ 1001.00  │ Representatives │ $1,001-$15,000   │ 1001  │ 15000 │ -15000 │ -1001 │
├────────────┼─────────────────────┼────────┼──────────────────────┼─────────────┼──────────┼─────────────────┼──────────────────┼───────┼───────┼────────┼───────┤
│ 2022-11-10 │ 2022-10-28 00:00:00 │ AAPL   │  Earl Blumenauer     │ Purchase    │ 15001.00 │ Representatives │ $15,001-$50,000  │ 15001 │ 50000 │ 15001  │ 50000 │
└────────────┴─────────────────────┴────────┴──────────────────────┴─────────────┴──────────┴─────────────────┴──────────────────┴───────┴───────┴────────┴───────┘
```

A breakdown of single-issue items the company is lobbying for will be printed by the command, `lobbying`:

```
(🦋) /stocks/gov/ $ lobbying
2022-10-20: APPLE INC. $50000
        Issues related to consumer electronics, software, the internet and STEM education.   H.R. 3843 - the Merger Filing Fee Modernization Act of 2021; H.R. 3460 - the State Antitrust Enforcement Venue Act of 2021 H.R. 3849 -the Augmenting Compatibility and Competition by Enabling Service Switching Act of 2021 or the ACCESS Act of 2021 H.R. 3826 - the Platform Competition and Opportunity Act of 2021 H.R. 3816 - the American Choice and Innovation Online Act H.R. 3825 - the Ending Platform Monopolies Act S.2992 - American Innovation and Choice Online Act S. 2710 - Open App Markets Act HR 5017 - Open App Markets Act S. 3830 - Fair Repair Act Privacy Legislation   Issues related to consumer electronics, software, the internet and STEM education.

2022-10-20: APPLE INC $1920000
        Providing information related to Apple Pay   Issues related to technology platform liability Issues related to content moderation   Issues related to transparency and government access to data, including H.R. 7072/S. 4373, the Non-Disclosure Order (NDO) Fairness Act   Issues related to the requirements of E.O. 14028, an Executive Order on Improving the Nation's Cybersecurity Issues related to cybersecurity requirements in H.R. 7900, the National Defense Authorization Act for Fiscal Year 2023   Issues related to the domestic manufacturing of semiconductors, including funding for the previously enacted CHIPS for America Act; S. 1260, the United States Innovation and Competition Act; and H.R. 4521, America COMPETES Act Providing information related to Apples supply chain   Issues related to immigration, including H.R. 6, the American Dream and Promise Act; S. 264, the Dream Act; H.R. 3648, the EAGLE Act; H.R. 5376, the Build Back Better Act; S. 2828, the Preserving Employment Visas Act; and S. 3721, the RELIEF Act Issues related to the Deferred Action for Childhood Arrivals program Issues related to waivers, recapturing unused green cards, and removing per-country caps on employment-based visas   Issues related to competition in digital markets and the app marketplace, including privacy, security, and competitiveness issues related to H.R. 3816/S. 2992, the American Choice and Innovation Online Act; H.R. 3849, the Augmenting Compatibility and Competition by Enabling Service Switching (ACCESS) Act; H.R. 3843, the Merger Filing Fee Modernization Act; H.R. 3460, the State Antitrust Enforcement Venue Act; and S. 2710/H.R. 7030, the Open App Markets Act Issues related to LGBTQ rights, including S. 393, the Equality Act   Providing information related to Apple Watch health features   General consumer privacy issues Providing information about online child safety Encouraging the development and adoption of strong consumer data privacy protections via legislation and/or regulatory policy H.R. 8152, the American Data Privacy and Protection Act Providing information on App Store policies and procedures   Issues related to the US-EU Privacy Shield Issues related to international discussions of digital regulation Issues related to anti-counterfeit policy, including provisions of S. 1260, the United States Innovation and Competition Act Issues related to the trade impacts of intellectual property disputes   Climate change Providing information on clean energy provisions in H.R. 5376, the Build Back Better Act   Providing general information about Apple's inclusion and diversity programs related to education Providing general information about Apple's coding and education programs and partnerships with community colleges, colleges and universities   General tax issues   General patent policy Issues related to standard essential patents Issues related to anti-counterfeit policy General trademark and copyright policy Issues related to patent proceedings and H.R. 5184, the Advancing Americas Interests Act

2022-10-20: APPLE INC. $90000
        Antitrust Issues, S. 2992- American Innovation and Choice Online Act, S. 2107 - FABS Act, S. 2710- Open App Markets Act, H.R.7030 - Open App Markets Act, General Business Issues, Intellectual Property Rights, H.R.4346 - Supreme Court Security Funding Act of 2022, Product Supply Chain Issues, Issues related to the domestic manufacturing of semiconductors, S.1260 - United States Innovation and Competition Act of 2021, H.R.4521 - United States Innovation and Competition Act of 2021

2022-10-20: APPLE INC. $110000
        Issues as they relate to technological goods and services; including S. 1260 - United States Innovation and Competition Act of 2021; S.2710 - Open App Markets Act of 2022; S.2992 - American Innovation and Choice Online Act of 2022; H.R. 3843 - the Merger Filing Fee Modernization Act of 2021; H.R. 3460 - the State Antitrust Enforcement Venue Act of 2021; H.R. 3849 - the Augmenting Compatibility and Competition by Enabling Service Switching Act of 2021; H.R. 3826 - the Platform Competition and Opportunity Act of 2021; H.R. 3816 - the American Choice and Innovation Online Act; H.R. 3825 - the Ending Platform Monopolies Act   Trade issues as they relate to technological goods and services; including S.2710 - Open App Markets Act of 2022; S.2992 - American Innovation and Choice Online Act of 2022; S. 1260 - United States Innovation and Competition Act of 2021; H.R. 3843 - the Merger Filing Fee Modernization Act of 2021; H.R. 3460 - the State Antitrust Enforcement Venue Act of 2021; H.R. 3849 - the Augmenting Compatibility and Competition by Enabling Service Switching Act of 2021; H.R. 3826 - the Platform Competition and Opportunity Act of 2021; H.R. 3816 - the American Choice and Innovation Online Act; H.R. 3825 - the Ending Platform Monopolies Act

2022-10-20: APPLE INC. $60000
        Issues related to spectrum and internet policy

2022-10-20: APPLE INC. $130000
        Educate policymakers regarding payments and financial technology regulation and issues around buy now pay later.   Educate policymakers regarding e-waste provisions, including in H.R. 5376, Inflation Reduction Act.   Monitor efforts to reform the Deferred Action for Childhood Arrivals program; monitor H.R. 6, the American Dream and Promise Act of 2021; and H.R. 1603, the Farm Workforce Modernization Act; monitor efforts to enact comprehensive immigration reform legislation, including S. 348 / H.R. 1177, to provide an earned path to citizenship, to address the root causes of migration and responsibly manage the southern border, and to reform the immigrant visa system, and for other purposes.   Educate policymakers on competition issues, including in S.2992/H.R.3816, American Choice and Innovation Online Act, S.2710/H.R.7030 Open App Markets Act, and H.R. 3843, the Merger Filing Fee Modernization Act of 2022.   Monitor online privacy, including H.R. 8152, the American Data Privacy and Protection Act; monitor issues related to online content moderation.

2022-10-18: COVINGTON & BURLING ON BEHALF OF APPLE INC. $60000
        Issues related to trade.   Issues related to public health matters.   Issues related to intellectual property.

2022-10-04: APPLE INC. $30000
        Competition issues in the consumer electronic, software, and internet sectors; S. 2992, the American Innovation and Choice Online Act; S. 2710, Open App Markets Act

2022-07-20: APPLE INC. $50000
        Issues related to consumer electronics, software, the internet and STEM education.   H.R. 3843 - the Merger Filing Fee Modernization Act of 2021; H.R. 3460 - the State Antitrust Enforcement Venue Act of 2021 H.R. 3849 -the Augmenting Compatibility and Competition by Enabling Service Switching Act of 2021 or the ACCESS Act of 2021 H.R. 3826 - the Platform Competition and Opportunity Act of 2021 H.R. 3816 - the American Choice and Innovation Online Act H.R. 3825 - the Ending Platform Monopolies Act S.2992 - American Innovation and Choice Online Act S. 2710 - Open App Markets Act HR 5017 - Open App Markets Act S. 3830 - Fair Repair Act Privacy Legislation   Issues related to consumer electronics, software, the internet and STEM education.

2022-07-20: APPLE INC. $90000
        Antitrust Issues, Cybersecurity, Privacy, Data Privacy Issues, S. 2992- American Innovation and Choice Online Act, S. 2107 - FABS Act, S. 2710- Open App Markets Act, H.R.7030 - Open App Markets Act, H.R.3816 - American Choice and Innovation Online Act, Manufacturing Issues
```

The consistency of quarterly contract awards over time is reflected in a chart requested by the command, `histcont`

![History of Quarterly Contracts Awarded to MSFT](https://user-images.githubusercontent.com/85772166/173206200-347aef6e-6b27-4bf8-9422-c03c5b414361.png)

The ten most purchased and sold stocks amongst Senate Representatives, `topsells senate` & `topbuys senate`:

![Senate's Most Bought and Sold Stocks](https://user-images.githubusercontent.com/85772166/173206214-964bfe40-a72c-4833-8cc1-a803bba97c6e.png)

To play a demonstration in the OpenBB Terminal of the features presented in this guide, execute the routine file, `gov_demo.openbb`, from the home menu.

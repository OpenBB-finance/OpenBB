---
title: Introduction to the Due Diligence Menu
keywords: "dd, due, diligence, dilligence, research, company, ticker, analyst, rating, rot, pt, est, sec, supplier, customer, arktrades, ratings, analysts, filings, form, forms, customers, suppliers"
date: "2022-06-01"
type: guides
status: publish
excerpt: "This guide introduces the Due Diligence menu within the Stocks menu, explains the features briefly, then provides examples."
geekdocCollapseSection: true
---

The Due Diligence submenu, located within the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">`Stocks`</a> menu, is primarily for supplementing fundamental analysis with information such as:

  - Analyst ratings and price targets over time
  - Earnings estimates
  - SEC filings
  - Business-to-business customers and suppliers
  - What kind of trades, if any, ARK is involved in with the loaded ticker.

To use all features in this menu, two (free) API keys must be obtained. Refer to the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/#accessing-other-sources-of-data-via-api-keys" target="_blank">Getting Started Guide</a> for instructions on storing API keys in the Terminal.

  - rating: FMP - <a href="https://site.financialmodelingprep.com/developer/docs/" target="_blank">Financial Modeling Prep</a>
  - rot: <a href="https://finnhub.io/" target="_blank">Finnhub</a>

Entering the submenu requires having a ticker <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/#explanation-of-commands" target="_blank">loaded</a> from the `Stocks` menu. With a stock selected, type `dd` into the command line and press `enter`.

![The Due Diligence submenu](https://user-images.githubusercontent.com/85772166/176110875-e23b0016-00a9-4fa0-b7e1-020a344c40ce.png)

<h2>How to use the Due Diligence Menu</h2>

With the same company, as loaded above, `sec -l 20` prints a table of the last twenty SEC filings from the company, and provides a link to a hosted document on <a href="https://marketwatch.com" target="_blank">MarketWatch</a>.

![Printing the last twenty SEC filings of CF Industries](https://user-images.githubusercontent.com/85772166/176111098-0a63a921-9695-422d-a495-0efdabafcd16.png)

`pt` displays a chart of historical adjusted closing prices and price targets. `pt --raw` prints a table, `pt --export xlsx` exports a spreadsheet, while `pt -l [n]` limits the number of price targets to return to `n`.

![Historical price targets for CF Industries](https://user-images.githubusercontent.com/85772166/176111207-4fe741a8-df49-4cbb-8216-94edebde77b7.png)

A new ticker can be loaded directly from the Due Diligence submenu; for example, `load tsla`

<h2>Examples</h2>

With $TSLA loaded, `arktrades -l 20`, shows the last twenty trades across all ARK funds.

![Last twenty Tesla trades across all ARK funds](https://user-images.githubusercontent.com/85772166/176111315-c79eee3a-d9cf-492b-9f07-8f0f6d08430a.png)

Export the history of $HOOD trades for further analysis. `arktrades --export xlsx`

![Robinhood trades across all ARK funds, exported](https://user-images.githubusercontent.com/85772166/176111475-2ba12aca-c0ba-4eb4-9751-dbd09fdd384c.png)

`est` displays futures earnings estimates.

![Hood quarterly earnings estimates](https://user-images.githubusercontent.com/85772166/176111584-3d51027e-7e3a-4579-8c40-14f59a40ce97.png)

![Hood annual earnings estimates](https://user-images.githubusercontent.com/85772166/176111708-3c88d7ce-f4e1-4e23-8107-dcf4e22869dc.png)

`analyst`

![Analyst coverage of Hood](https://user-images.githubusercontent.com/85772166/176111824-1133da8e-18e4-4b12-baa4-7a5d4b77e784.png)

Always do your own Due Diligence! To run a demo in the OpenBB Terminal of the features discussed here, launch the routine from the Main Menu by entering: `exe routines/dd_demo.openbb` in the command line and hitting `enter`. Click <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">here</a> to go back to `Stocks`.

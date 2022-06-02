---
title: Introduction to Comparison Analysis
keywords: "Comparison, analysis, ca, menu, submenu, stocks, compare, correlation, similar, historical, hcorr, volume, income, balance, cashflow, sentiment, scorr, overview, valuation, financial, ownership, performance, technical, tsne, getpoly, getfunnhub, getfinviz, set, add, rmv, Polygon, Finnhub, Finviz, Yahoo, yFinance, FinBrain, market, watch "
date: "2022-05-27"
type: guides
status: publish
excerpt: "An Introduction to Comparison Analysis, within the Stocks Menu, with a brief overview of the features."
geekdocCollapseSection: true
---
The Comparison Analysis menu provides the user with tools for:
  - searching and populating a list of companies that are similar to the loaded ticker.
  - building a correlation matrix.
  - comparing the price and volume history of multiple companies.
  - comparing financial statements, technical performance, and ownership statistics of otherwise similar companies.
  - comparing sentiment of similar companies.
  - building a list of companies to use features from the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/portfolio/po/" target="_blank">Portfolio Optimization menu</a>.

To use all features in this menu, the following <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/#accessing-other-sources-of-data-via-api-keys" target="_blank">API keys (free)</a> must be obtained by the user:

  - <a href="https://finnhub.io/" target="_blank">Finnhub</a> `getfinnhub`
  - <a href="https://polygon.io/" target="_blank">Polygon</a> `getpoly`

It is not necessary to load a ticker from the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">stocks</a> menu to use these features. Enter the Comparison Analysis submenu by typing `ca` and pressing `ENTER` (⏎).

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171148283-2cbb5942-dc56-4276-a30c-7cbc045627a1.png"><img alt="Comparison Analysis Menu" src="https://user-images.githubusercontent.com/46355364/171148283-2cbb5942-dc56-4276-a30c-7cbc045627a1.png"></a>

## How to use

To add a primary ticker, or to swap it for another, enter `ticker AMZN`. The three commands: `getfinnhub`, `getpoly`
and `getfinviz` all provide a similar function. Sources may return different results.

````
(🦋) /stocks/ca/ $ getfinviz
[Finviz] Similar Companies: WMT, BIG, BJ, COST, DG, DLTR, OLLI, PSMT, TGT, TUEM 

(🦋) /stocks/ca/ $ getpoly
[Polygon] Similar Companies: WMT, AMZN, COST, EBAY, DLTR, KSS, JCP, TGT, M, DG

(🦋) /stocks/ca/ $ getfinnhub
[Finnhub] Similar Companies: WMT, COST, BJ, PSMT
````
Using any of these commands will automatically populate the list of similar companies for analysis. Furthermore, `add` & `rmv` allows the user to make modifications, or create a list from scratch.

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171148589-08cc106f-4e1d-4d94-92b5-09190f1798d4.png"><img alt="Get similar companies for analysis" src="https://user-images.githubusercontent.com/46355364/171148589-08cc106f-4e1d-4d94-92b5-09190f1798d4.png"></a>

To show a correlation matrix, use the `hcorr` command. The start dates can be modified, which changes the results, to show correlation over different periods. For example, obtain a one year correlation matrix with `hcorr`:

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171148882-a0f1c57a-6761-4fbc-a03f-e5213a52c7f0.png"><img alt="One year correlation matrix" src="https://user-images.githubusercontent.com/46355364/171148882-a0f1c57a-6761-4fbc-a03f-e5213a52c7f0.png"></a>

Or, by adjusting the date, it is possible to define a correlation matrix with a different time horizon, e.g `hcorr -s 2022-01-01`:

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171149853-1a84e9af-7099-4a72-b687-01f2e32d0485.png"><img alt="YTD correlation matrix" src="https://user-images.githubusercontent.com/46355364/171149853-1a84e9af-7099-4a72-b687-01f2e32d0485.png"></a>

The list of similar companies can be compared by a number of fundamental metrics. 

`valuation` displays earnings and valuation multiples.
<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171150439-31cbe514-e676-4814-8b4b-a6087e2d417a.png"><img alt="Valuation" src="https://user-images.githubusercontent.com/46355364/171150439-31cbe514-e676-4814-8b4b-a6087e2d417a.png"></a>

`performance` compares technical performance of similar companies:
<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171150577-9333c3a2-a60e-47e9-86e9-206187744b2a.png"><img alt="Performance" src="https://user-images.githubusercontent.com/46355364/171150577-9333c3a2-a60e-47e9-86e9-206187744b2a.png"></a>

`sentiment` is a chart from  <a href="https://finbrain.tech" target="_blank">Finbrain</a> that shows sentiment over the last ten days.
<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171150795-cdff5c5e-c0c8-4ca3-ba60-3f148ba80a22.png"><img alt="Performance" src="https://user-images.githubusercontent.com/46355364/171150795-cdff5c5e-c0c8-4ca3-ba60-3f148ba80a22.png"></a>

This list of similar companies can be imported directly to the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/portfolio/po/" target="_blank">Portfolio Optimization</a> menu by using the command, `po`.
<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171150890-e96722cd-6f18-41a3-b720-bbb3ecaeb4c8.png"><img alt="PO Menu" src="https://user-images.githubusercontent.com/46355364/171150890-e96722cd-6f18-41a3-b720-bbb3ecaeb4c8.png"></a>

## Examples

The correlation matrix can also be used in other ways, like measuring sectors or asset classes. The chart below is a daily, price-normalized, comparison of S&P, NASDAQ, and BTC futures.

````
(🦋) /stocks/ca/ $ add es=f
[Custom] Similar Companies: ES=F, NQ=F, BTC=F 

(🦋) /stocks/ca/ $ historical -n
````
<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171151014-ce034108-7efd-456c-b37a-f41fb6b8aa91.png"><img alt="Historical" src="https://user-images.githubusercontent.com/46355364/171151014-ce034108-7efd-456c-b37a-f41fb6b8aa91.png"></a>

This is a chart of the NASDAQ 100 Index, and three different futures contracts that are trading against it.

````
(🦋) /stocks/ca/ $ set ^NDX,NQH23.CME,NQZ22.CME,NQ=F
[Custom] Similar Companies: ^NDX, NQH23.CME, NQZ22.CME, NQ=F 

(🦋) /stocks/ca/ $ historical
````
<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171151179-3aa6c72c-0590-4926-9b47-f1741c87813a.png"><img alt="Historical NASDAQ 100" src="https://user-images.githubusercontent.com/46355364/171151179-3aa6c72c-0590-4926-9b47-f1741c87813a.png"></a>

Compare financial statements of the ten largest US banks.
````
(🦋) /stocks/ca/ $ set C,USB,WFC,JPM,TD,GS,PNC,TFC,BAC,COF
[Custom] Similar Companies: C, USB, WFC, JPM, TD, COF, PNC, TFC, BAC, GS 
(🦋) /stocks/ca/ $ cashflow
````
<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171151317-5077646d-7488-46ae-9899-515d49f0f114.png"><img alt="Cashflow comparison of the ten largest US banks" src="https://user-images.githubusercontent.com/46355364/171151317-5077646d-7488-46ae-9899-515d49f0f114.png"></a>

Compare the income statements.

````
(🦋) /stocks/ca/ $ income
````
<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171151496-ea1d07ab-de45-4cf0-aa3e-5119101ef861.png"><img alt="Income statements of the ten largest US banks" src="https://user-images.githubusercontent.com/46355364/171151496-ea1d07ab-de45-4cf0-aa3e-5119101ef861.png"></a>

To run a demonstration of the commands presented here, in the OpenBB Terminal, run this command from the home menu: `exe routines/comparison_demo.openbb`

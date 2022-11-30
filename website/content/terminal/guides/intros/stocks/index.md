---
title: Stocks
keywords: ["stocks", "fundamental", "analysis", "technical", "analysis", "analyst", "equity", "research"]
excerpt: "The Introduction to Stocks explains how to use the
menu and provides a brief description of its sub-menus"

---

The Stocks menu enables you to perform an evaluation of a particular company, a sector or a market as whole by performing various techniques including fundamental, technical and behavioural analysis. It does so by handing you tools to (among other things) evaluate company news (<a href="/terminal/reference/stocks/news/" target="_blank" rel="noreferrer noopener">news</a>), display historic quarterly results (<a href="/terminal/reference/stocks/fa/income/" target="_blank" rel="noreferrer noopener">income</a>), determine future cash flows (<a href="/terminal/reference/stocks/fa/dcf/" target="_blank" rel="noreferrer noopener">dcf</a>),
show analyst recommendations (<a href="/terminal/reference/stocks/dd/pt/" target="_blank" rel="noreferrer noopener">pt</a>), evaluate an entire sector or industry (<a href="/terminal/reference#sia" target="_blank" rel="noreferrer noopener">sia</a>), and show the historical prices, correlations and sentiment between similar companies (<a href="/terminal/reference/stocks/ca/hcorr/" target="_blank" rel="noreferrer noopener">correlation</a>).

### How to use

The Stocks menu is called upon by typing `stocks` which opens the following menu:

![Stocks Menu](https://user-images.githubusercontent.com/46355364/169503852-e8ebe577-6e49-438a-b14a-606c9fb9a6de.png)

You have the ability to <a href="/terminal/reference/stocks/search/" target="_blank" rel="noreferrer noopener">search</a> a stock based on a search criteria, country, sector or industry. An example:

```
2022 May 17, 08:45 (🦋) /stocks/ $ search facebook
                                                      Companies found on term facebook
--------------------------------------------------------------------------------------------------------------------------------------------
|           | Name                              | Country       | Sector                 | Industry                       | Exchange       |
------------|-----------------------------------|---------------|------------------------|--------------------------------|----------------|
| FB.BA     | Facebook, Inc.                    | United States | Communication Services | Internet Content & Information | Argentina      |
|-----------|-----------------------------------|---------------|------------------------|--------------------------------|----------------|
| FB.MI     | Facebook, Inc.                    | United States | Communication Services | Internet Content & Information | Italy          |
|-----------|-----------------------------------|---------------|------------------------|--------------------------------|----------------|
| FB.MX     | Facebook, Inc.                    | United States | Communication Services | Internet Content & Information | Mexico         |
|-----------|-----------------------------------|---------------|------------------------|--------------------------------|----------------|
| FB        | Facebook, Inc.                    | United States | Communication Services | Internet Content & Information | USA            |
|-----------|-----------------------------------|---------------|------------------------|--------------------------------|----------------|
| FB.SN     | Facebook, Inc.                    | United States |                        |                                | Chile          |
|-----------|-----------------------------------|---------------|------------------------|--------------------------------|----------------|
| FB.VI     | Facebook, Inc.                    | United States | Communication Services | Internet Content & Information | Austria        |
|-----------|-----------------------------------|---------------|------------------------|--------------------------------|----------------|
| FB2.L     | Leverage Shares 2x Facebook ETC A | None          | None                   | None                           | United-Kingdom |
|-----------|-----------------------------------|---------------|------------------------|--------------------------------|----------------|
| FB2A.DE   | Facebook, Inc.                    | United States | Communication Services | Internet Content & Information | Germany        |
|-----------|-----------------------------------|---------------|------------------------|--------------------------------|----------------|
| FB2A.F    | Facebook, Inc.                    | United States | Communication Services | Internet Content & Information | Germany        |
|-----------|-----------------------------------|---------------|------------------------|--------------------------------|----------------|
| FB3.L     | Leverage Shares 3x Facebook ETC   | None          | None                   | None                           | United-Kingdom |
|-----------|-----------------------------------|---------------|------------------------|--------------------------------|----------------|
| FBOK34.SA | Facebook, Inc.                    | United States | Communication Services | Internet Content & Information | Brazil         |
|-----------|-----------------------------------|---------------|------------------------|--------------------------------|----------------|
| FBS.L     | Leverage Shares -1x Facebook ETC  | None          | None                   | None                           | United-Kingdom |
|-----------|-----------------------------------|---------------|------------------------|--------------------------------|----------------|
| SFB.L     | Leverage Shares -1x Facebook ETC  | None          | None                   | None                           | United-Kingdom |
--------------------------------------------------------------------------------------------------------------------------------------------
```

This results in a selection of <a href="https://www.investopedia.com/ask/answers/12/what-is-a-stock-ticker.asp" target="_blank" rel="noreferrer noopener">stock tickers</a> and their corresponding exchange. With this information, you can load in one of the stock tickers into the menu. This can be done with <a href="/terminal/reference/stocks/load/" target="_blank" rel="noreferrer noopener">load</a>. See the following example:

```
2022 May 17, 08:46 (🦋) /stocks/ $ load FB

Loading Daily FB stock with starting period 2019-05-13 for analysis.

Datetime: 2022 May 17 08:49
Timezone: America/New_York
Currency: USD
Market:   OPEN
Company:  Meta Platforms, Inc.

                                           FB Performance
----------------------------------------------------------------------------------------------------
| 1 Day | 1 Week | 1 Month | 1 Year   | YTD      | Volatility (1Y) | Volume (10D avg) | Last Price |
--------|--------|---------|----------|----------|-----------------|------------------|------------|
| 4.6 % | 1.95 % | -4.82 % | -36.59 % | -40.91 % | 38.04 %         | 39.8 M           | 200.04     |
----------------------------------------------------------------------------------------------------
```

To then view the stock chart, you can call <a href="/terminal/reference/stocks/candle/" target="_blank" rel="noreferrer noopener">candle</a> which shows a candle chart for the defined period:

<img src="https://user-images.githubusercontent.com/46355364/169503942-f3f05bbe-77f1-443e-945e-cafbe442bce8.png" alt="Candle Chart Facebook" width="800"/>

By calling `?` or `help` the stocks menu re-appears. Here you can see that multiple menus have turned blue. Because of loading a stock ticker, these menus can now be used in combination with the chosen stock.

<img src="https://user-images.githubusercontent.com/46355364/169503960-62a59aa2-1dbd-46f1-9ea0-095817d7da5d.png" alt="Stocks Menu with Ticker" width="800"/>

### Sub-menus available

The Stock menu has an extensive list of available sub-menus ranging from fundamental analysis to sector analysis to advanced prediction techniques. To find more information about each menu, click on one of the following:

- <a href="/terminal/guides/intros/stocks/tradinghours" target="_blank" rel="noreferrer noopener">Introduction to Trading Hours</a>: discover exchanges that are currently open or closed for a specified ticker. Also find relevant information about each exchange.
- <a href="/terminal/guides/intros/stocks/options" target="_blank" rel="noreferrer noopener">Introduction to Options</a>: look into available options, option spreads, open interest and binomial valuation models.
- <a href="/terminal/guides/intros/stocks/disc" target="_blank" rel="noreferrer noopener">Introduction to Stock Discovery</a>: discover trending stocks based on return metrics, revenue and earnings growth, penny stocks and based on upcoming earnings release dates.
- <a href="/terminal/guides/intros/stocks/sia" target="_blank" rel="noreferrer noopener">Introduction to Sector & Industry Analysis</a>: analyse companies that reside in the same industry, sector and/or country and share a similar market cap to determine potential under- and out performance of each company.
- <a href="/terminal/guides/intros/stocks/dark-pool-shorts" target="_blank" rel="noreferrer noopener">Introduction to Dark Pools</a>: discover companies that have enormous shorting pressure, obtain information about dark pool positions and find out about shares that failed to deliver.
- <a href="/terminal/guides/intros/stocks/screener" target="_blank" rel="noreferrer noopener">Introduction to Stock Screener</a>: provides the ability to screen companies that share a similar characteristic, for example unusual volumes, overbought or that include analyst upgrades, and be able to compare valuations and performance.
- <a href="/terminal/guides/intros/stocks/ins" target="_blank" rel="noreferrer noopener">Introduction to Insider Trading</a>: explains what large insiders, e.g. a CEO of a company, is buying the chosen company and insider trading activity for the chosen company.
- <a href="/terminal/guides/intros/stocks/gov" target="_blank" rel="noreferrer noopener">Introduction to Government</a>: gives insights in what the House of Congress is trading and the corporate lobbying that is performed.
- <a href="/terminal/guides/intros/common/ba" target="_blank" rel="noreferrer noopener">Introduction to Behavioural Analysis</a>: gives the abilities to discover how different social media platforms view the chosen company and what is written about them.
- <a href="/terminal/guides/intros/stocks/comparison" target="_blank" rel="noreferrer noopener">Introduction to Comparison Analysis</a>: have the ability to compare companies based on, among other things, correlation, financial statements, sentiment, valuations and performance.
- <a href="/terminal/guides/intros/stocks/fa" target="_blank" rel="noreferrer noopener">Introduction to Fundamental Analysis</a>: look into the fundamentals of a chosen company including financial statements, SEC filings, investing scores, discounted cash flow analysis (DCF), sustainability scores and key ratios.
- <a href="/terminal/guides/intros/stocks/dd" target="_blank" rel="noreferrer noopener">Introduction to Due Diligence</a>: explore analyst recommendations, ratings over time, price targets and quarterly and yearly earnings estimates.
- <a href="/terminal/guides/intros/common/ta" target="_blank" rel="noreferrer noopener">Introduction to Technical Analysis</a>: analysis the chosen company's historical data extensively with moving averages and momentum, trend, volatility and volume indicators.
- <a href="/terminal/guides/intros/common/qa" target="_blank" rel="noreferrer noopener">Introduction to Quantitative Analysis</a>: delve deeper in the historical data with quantitative methods including cumulative distribution function (CDF), (conditional) Value at Risk and rolling ratios.
- <a href="/terminal/guides/intros/forecast/" target="_blank" rel="noreferrer noopener">Introduction to Forecasting menu</a>: apply advanced AI and Machine Learning models to form prediction of future stock prices including Recurrent Neural Network (RNN), Autoregressive Integrated Moving Average (ARIMA) and Monte Carlo forecasting.

### Examples

If we want to a look at the historical data and fundamentals of Microsoft, we can do the following, starting from the `stocks` menu. First, load in the ticker of Microsoft, this is `MSFT` and can be found with the <a href="/terminal/reference/stocks/search/" target="_blank" rel="noreferrer noopener">search</a> command:

```
2022 May 18, 05:32 (🦋) /stocks/ $ search microsoft
```

<p align="center">Companies found with the term 'microsoft'</p>

|           | Name                               | Country       | Sector     | Industry                  | Exchange       |
| --------- | ---------------------------------- | ------------- | ---------- | ------------------------- | -------------- |
| MSF.BR    | Microsoft Corporation              | United States | Technology | Software - Infrastructure | Belgium        |
| MSF.DE    | Microsoft Corporation              | United States | Technology | Software - Infrastructure | Germany        |
| MSF.F     | Microsoft Corporation              | United States | Technology | Software - Infrastructure | Germany        |
| MSF2.L    | Leverage Shares 2x Microsoft ETC A | None          | None       | None                      | United-Kingdom |
| MSF3.L    | Leverage Shares 3x Microsoft ETC   | None          | None       | None                      | United-Kingdom |
| MSFS.L    | Leverage Shares -1x Microsoft ETC  | None          | None       | None                      | United-Kingdom |
| MSFT.BA   | Microsoft Corporation              | United States | Technology | Software - Infrastructure | Argentina      |
| MSFT.MX   | Microsoft Corporation              | United States | Technology | Software - Infrastructure | Mexico         |
| MSFT      | Microsoft Corporation              | United States | Technology | Software - Infrastructure | USA            |
| MSFT.SN   | Microsoft Corporation              | United States | Technology | Software - Infrastructure | Chile          |
| MSFT.VI   | Microsoft Corporation              | United States | Technology | Software - Infrastructure | Austria        |
| MSFT34.SA | Microsoft Corporation              | United States | Technology | Software - Infrastructure | Brazil         |
| SMSF.L    | Leverage Shares -1x Microsoft ETC  | None          | None       | None                      | United-Kingdom |

Then, load in the historical data of the company by using the <a href="/terminal/reference/stocks/load/" target="_blank" rel="noreferrer noopener">load</a>. We also choose a different starting period by using `-s` as shown in the documentation:

```
2022 May 18, 05:43 (🦋) /stocks/ $ load MSFT -s 2021-01-01

Loading Daily MSFT stock with starting period 2021-01-01 for analysis.

Datetime: 2022 May 18 05:43
Timezone: America/New_York
Currency: USD
Market:   OPEN
Company:  Microsoft Corporation

                                          MSFT Performance
-----------------------------------------------------------------------------------------------------
| 1 Day  | 1 Week  | 1 Month | 1 Year  | YTD      | Volatility (1Y) | Volume (10D avg) | Last Price |
---------|---------|---------|---------|----------|-----------------|------------------|------------|
| 2.18 % | -0.99 % | -4.88 % | 10.66 % | -20.13 % | 24.31 %         | 39.77 M          | 266.82     |
-----------------------------------------------------------------------------------------------------
```

We can now plot the corresponding stock chart with <a href="/terminal/reference/stocks/candle/" target="_blank" rel="noreferrer noopener">candle</a> which shows the company's historical data from 2021-01-01 until the current date. We are also adding in the 20 and 30 day <a href="https://www.investopedia.com/terms/m/movingaverage.asp" target="_blank" rel="noreferrer noopener">moving averages (MA)</a>.

```
2022 May 18, 05:44 (🦋) /stocks/ $ candle --ma 20,30
```

![Candle Chart Microsoft with Moving Average](https://user-images.githubusercontent.com/46355364/169504138-ca51c824-c2d1-428f-90b4-77b7b021718e.png)

Now we can go ahead and enter the Fundamental Analysis menu by typing `fa`. Please see <a href="/terminal/guides/intros/fa" target="_blank" rel="noreferrer noopener">Introduction to Fundamental Analysis</a> for a more detailed guide on this menu. This will open the following:

![Fundamental Analysis Menu](https://user-images.githubusercontent.com/46355364/169504216-17484f7d-9cc5-4a56-9c62-d79cde79e91d.png)

Within this menu, I am now able to present the quarterly income statements over the last 3 years (or any other period) by using <a href="/terminal/reference/stocks/fa/income/" target="_blank" rel="noreferrer noopener">income</a>.

```
2022 May 18, 05:52 (🦋) /stocks/fa/ $ income -q -l 12
                                                                                  MSFT Income Statement

|                            | 2019-06-30 | 2019-09-30 | 2019-12-31 | 2020-03-31 | 2020-06-30 | 2020-09-30 | 2020-12-31 | 2021-03-31 | 2021-06-30 | 2021-09-30 | 2021-12-31 | 2022-03-31 |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Reported Currency          | USD        | USD        | USD        | USD        | USD        | USD        | USD        | USD        | USD        | USD        | USD        | USD        |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Gross Profit               | 23.305 B   | 22.649 B   | 24.548 B   | 24.046 B   | 25.694 B   | 26.152 B   | 28.882 B   | 28.661 B   | 32.161 B   | 31.671 B   | 34.768 B   | 33.745 B   |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Total Revenue              | 33.717 B   | 32.428 B   | 36.322 B   | 34.315 B   | 38.033 B   | 36.724 B   | 42.558 B   | 41.059 B   | 45.595 B   | 44.743 B   | 51.228 B   | 48.732 B   |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Cost Of Revenue            | 17.199 B   | 16.363 B   | 18.986 B   | 17.650 B   | 20.161 B   | 16.941 B   | 20.907 B   | 20.070 B   | 22.025 B   | 20.145 B   | 24.433 B   | 23.481 B   |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Costof Goods And Services  | 10.412 B   | 10.406 B   | 12.358 B   | 10.975 B   | 12.339 B   | 11.002 B   | 14.194 B   | 13.045 B   | 13.991 B   | 13.646 B   | 16.960 B   | 15.615 B   |
| Sold                       |            |            |            |            |            |            |            |            |            |            |            |            |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Operating Income           | 12.405 B   | 12.686 B   | 13.891 B   | 12.975 B   | 13.407 B   | 15.876 B   | 17.897 B   | 17.048 B   | 19.095 B   | 20.238 B   | 22.247 B   | 20.364 B   |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Selling General And        | 6.387 B    | 5.398 B    | 6.054 B    | 6.184 B    | 7.073 B    | 5.350 B    | 6.086 B    | 6.409 B    | 7.379 B    | 5.834 B    | 6.763 B    | 7.075 B    |
| Administrative             |            |            |            |            |            |            |            |            |            |            |            |            |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Research And Development   | 4.513 B    | 4.565 B    | 4.603 B    | 4.887 B    | 5.214 B    | 4.926 B    | 4.899 B    | 5.204 B    | 5.687 B    | 5.599 B    | 5.758 B    | 6.306 B    |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Operating Expenses         | 11.300 B   | 10.522 B   | 11.231 B   | 11.562 B   | 13.036 B   | 10.865 B   | 11.612 B   | 12.229 B   | 13.721 B   | 12.098 B   | 13.231 B   | 14.172 B   |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Investment Income Net      | 709 M      | 724 M      | 688 M      | 673 M      | 595 M      | 570 M      | 545 M      | 519 M      | 497 M      | 520 M      | 503 M      | 519 M      |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Net Interest Income        | -669 M     | -637 M     | -654 M     | -614 M     | -686 M     | -589 M     | -571 M     | -633 M     | -553 M     | -539 M     | -525 M     | -503 M     |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Interest Income            | 321 M      | -139 M     | 281 M      | -153 M     | None       | None       | 545 M      | 519 M      | 497 M      | 520 M      | 503 M      | 519 M      |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Interest Expense           | 669 M      | 637 M      | 654 M      | 614 M      | 686 M      | 589 M      | 571 M      | 633 M      | 553 M      | 539 M      | 525 M      | 503 M      |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Non Interest Income        | 33.717 B   | 33.065 B   | 36.976 B   | 34.929 B   | 38.033 B   | 37.313 B   | 43.129 B   | 41.692 B   | 46.148 B   | 45.282 B   | 51.753 B   | 49.235 B   |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Other Non Operating Income | -121 M     | -18 M      | -19 M      | -3 M       | 0          | 0          | 70 M       | 6 M        | 22 M       | 6 M        | -4 M       | -11 M      |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Depreciation               | None       | None       | None       | None       | None       | None       | None       | None       | None       | None       | None       | None       |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Depreciation And           | 400 M      | 559 M      | 574 M      | 491 M      | 588 M      | 589 M      | 627 M      | 616 M      | 655 M      | 665 M      | 710 M      | 791 M      |
| Amortization               |            |            |            |            |            |            |            |            |            |            |            |            |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Income Before Tax          | 12.596 B   | 12.686 B   | 14.085 B   | 12.843 B   | 13.422 B   | 16.124 B   | 18.337 B   | 17.236 B   | 19.405 B   | 20.524 B   | 22.515 B   | 20.190 B   |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Income Tax Expense         | -591 M     | 2.008 B    | 2.436 B    | 2.091 B    | 2.220 B    | 2.231 B    | 2.874 B    | 1.779 B    | 2.947 B    | 19 M       | 3.750 B    | 3.462 B    |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Interest And Debt Expense  | 669 M      | 637 M      | 654 M      | 614 M      | 686 M      | 589 M      | 571 M      | 633 M      | 553 M      | 539 M      | 525 M      | 503 M      |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Net Income From Continuing | 12.405 B   | 10.678 B   | 11.649 B   | 10.752 B   | 13.407 B   | 13.893 B   | 15.463 B   | 15.457 B   | 16.458 B   | 20.505 B   | 18.765 B   | 16.728 B   |
| Operations                 |            |            |            |            |            |            |            |            |            |            |            |            |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Comprehensive Income Net   | 14.112 B   | 10.957 B   | 11.455 B   | 13.683 B   | 11.712 B   | 13.807 B   | 15.720 B   | 13.552 B   | 16.818 B   | 19.966 B   | 17.919 B   | 13.815 B   |
| Of Tax                     |            |            |            |            |            |            |            |            |            |            |            |            |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Ebit                       | 13.265 B   | 13.323 B   | 14.739 B   | 13.457 B   | 14.108 B   | 16.713 B   | 18.908 B   | 17.869 B   | 19.958 B   | 21.063 B   | 23.040 B   | 20.693 B   |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Ebitda                     | 13.665 B   | 13.882 B   | 15.313 B   | 13.948 B   | 14.696 B   | 17.302 B   | 19.535 B   | 18.485 B   | 20.613 B   | 21.728 B   | 23.750 B   | 21.484 B   |
|----------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| Net Income                 | 13.187 B   | 10.678 B   | 11.649 B   | 10.752 B   | 11.202 B   | 13.893 B   | 15.463 B   | 15.457 B   | 16.458 B   | 20.505 B   | 18.765 B   | 16.728 B   |
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

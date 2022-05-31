---
title: Introduction to Dark Pools & Short Data
keywords: "darkpools, dps, dark, pools, dp, short, shorts, naked, selling, sales, SEC, disclosure, ATS, OTC, OTCE, NMS, borrowed, shorted, ftd, fails-to-deliver, volume"
date: "05-30-2022"
type: guides
status: publish
excerpt: "The Introduction to Dark Pools & Short Data, within the Stocks menu, which explains how to use the menu and
provides a brief explanation of the features."
geekdocCollapseSection: true
---
Dark Pools and short selling are both, controversial and mysterious, subjects. The lack of disclosure for short sales and dark pool trades makes a lot of guess-work. It is a good idea to read through some research on the topic available from the SEC:
  - <a href="https://www.sec.gov/marketstructure/research/ats_data_paper_october_2013.pdf" target="_blank">Alternative Trading Systems: Description of ATS Trading in National Market System Stocks</a>
  - <a href="https://www.sec.gov/news/statement/shedding-light-on-dark-pools.html" target="_blank">Shedding Light on Dark Pools</a>
  - <a href="https://www.sec.gov/dera/staff-papers" target="_blank">Staff Papers and Analyses</a>

The purpose of this menu is to provide the user with tools for gauging the level of short interest, FTD rate, and off-exchange volume in a <a href="https://www.law.cornell.edu/cfr/text/17/242.600" target="_blank">NMS security</a>.
There are also commands for looking at market as a whole. Enter the submenu from the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">Stocks menu</a> by typing, `dps`, and hitting `ENTER` (⏎).

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171151760-9f65424e-b4d6-41a7-b31f-e9bc1c723bd9.png"><img alt="The Dark Pools Menu" src="https://user-images.githubusercontent.com/46355364/171151760-9f65424e-b4d6-41a7-b31f-e9bc1c723bd9.png"></a>

To use every feature in the Dark Pools menu, an API key for <a href="https://www.quandl.com/" target="_blank">Quandl</a> must be obtained (for free) and authorized on the local installation. See the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/#accessing-other-sources-of-data-via-api-keys" target="_blank">Getting Started Guide</a> for help setting up the API keys in the OpenBB Terminal. The four commands at the bottom of the menu rely on a loaded ticker while the six above do not.

## How to use

The commands which are not ticker-specific provide screener-like utility. A list of the most-shorted stocks, according to Yahoo Finance, is displayed with the `shorted` command. It should be noted that this menu is only able to provide data for SEC-regulated equities.

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171168215-ce1384ec-c3d6-4ff5-a97f-cd60f3a7d38e.png"><img alt="shorted command output" src="https://user-images.githubusercontent.com/46355364/171168215-ce1384ec-c3d6-4ff5-a97f-cd60f3a7d38e.png"></a>

`hsi` is another <a href="https://highshortinterest.com" target="_blank">source</a> for the same list. There will be slight variations between the two.

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171168329-a9b2ec6e-b87c-4e35-aca9-b3ff73947ffe.png"><img alt="hsi command output" src="https://user-images.githubusercontent.com/46355364/171168329-a9b2ec6e-b87c-4e35-aca9-b3ff73947ffe.png"></a>

`prom` performs a linear regression to scan for tickers with growing trade activity on ATS tapes, reported to <a href="https://otctransparency.finra.org/otctransparency/AtsIssueData" target="_blank">FINRA</a>.

````
(🦋) /stocks/dps/ $ prom -n 50 -l 5 -t T1
Processing Tier T1 ...
Processing regression on 50 promising tickers ...
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171168513-2d57fdd6-041f-4ba1-99b3-6168f2141193.png"><img alt="Growing ATS Tier 1 NMS Trading Activity" src="https://user-images.githubusercontent.com/46355364/171168513-2d57fdd6-041f-4ba1-99b3-6168f2141193.png"></a>

Tier 2 NMS Tickers:
````
(🦋) /stocks/dps/ $ prom -n 50 -l 5 -t T2
Processing Tier T2 ...
Processing regression on 50 promising tickers ...
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171168676-1fa22167-3312-4e06-b5f5-261b13c45cf8.png"><img alt="Growing ATS Tier 2 NMS Trading Activity" src="https://user-images.githubusercontent.com/46355364/171168676-1fa22167-3312-4e06-b5f5-261b13c45cf8.png"></a>

Tier 3 OTCE Tickers:
````
(🦋) /stocks/dps/ $ prom -n 50 -l 5 -t OTCE
Processing Tier OTCE ...
Processing regression on 50 promising tickers ...
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171168812-2e8dce0c-c81a-4de8-9442-7f1e2ae76da8.png"><img alt="Growing ATS OTCE NMS Trading Activity" src="https://user-images.githubusercontent.com/46355364/171168812-2e8dce0c-c81a-4de8-9442-7f1e2ae76da8.png"></a>

`pos` provides a summary for the last reported trading day (information is updated in the early evening). Position represents a rolling twenty-day total and directional trends can be identified by watching the changes over time. Adding the `-a` flag will sort the list from the bottom up - the most negative - and creates a fuller picture when watching in tandom with the positive side of the ledger. Monitor the rate of change in position sizes, or a reversal in directional flow. This <a href="https://squeezemetrics.com/monitor/download/pdf/short_is_long.pdf?" target="_blank">white paper</a>, written by SqueezeMetrics, sheds some light on the trading activity reported here.

````
(🦋) /stocks/dps/ $ pos -l 25
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171168989-946b0efc-6ebf-4d1c-aea4-5a7071b577b6.png"><img alt="Top 25 Dark Pool Positions" src="https://user-images.githubusercontent.com/46355364/171168989-946b0efc-6ebf-4d1c-aea4-5a7071b577b6.png"></a>

The other end of the spectrum:

````
(🦋) /stocks/dps/ $ pos -l 25 -a
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171169207-cb33a6b1-488c-43a8-bd9a-c5704a815a87.png"><img alt="Top 25 Dark Pool Positions" src="https://user-images.githubusercontent.com/46355364/171169207-cb33a6b1-488c-43a8-bd9a-c5704a815a87.png"></a>

Call on the help dialogue for every command by attaching, `-h` to the command. The optional arguments give the user flexibility to sort the columns, print the raw data, or export to a file.

## Examples

The cost-to-borrow is used as a proxy-measurement for an equity's specialness. `ctb` shows the  most expensive equities to short, and the number shares available to short, on Interactive Brokers.

````
(🦋) /stocks/dps/ $ ctb
````


<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171169317-c154f61c-9e79-4fdd-b867-395c77e3efeb.png"><img alt="ctb" src="https://user-images.githubusercontent.com/46355364/171169317-c154f61c-9e79-4fdd-b867-395c77e3efeb.png"></a>

How many tickers have a borrow rate above 100%? Set the limit to a high number and export the data to a spreadsheet.

````
(🦋) /stocks/dps/ $ ctb -n 5000 --export xlsx

Saved file: /exports/20220530_130058_stocks_dark_pool_shorts_cost_to_borrow.xlsx
````

As of writing, there are 158 securities with a cost-to-borrow rate above 100%.

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171169650-d5da6249-a3b5-4130-be71-8bb9d78057e8.png"><img alt="ctb2" src="https://user-images.githubusercontent.com/46355364/171169650-d5da6249-a3b5-4130-be71-8bb9d78057e8.png"></a>

Cross reference that list with the `sidtc` command. Days-to-cover is the approximate number of days it would take to cover those shorts if the amount and proportion of volume were to remain constant. Use the optional arguments to sort the columns.

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171169807-5de8c8be-c822-4c04-8e82-11ba351bace8.png"><img alt="sidtc" src="https://user-images.githubusercontent.com/46355364/171169807-5de8c8be-c822-4c04-8e82-11ba351bace8.png"></a>

Load AAPL and request a 1-year chart of the net short volume and position. This provides the individual ticker data corresponding with the `pos` command.

````
(🦋) /stocks/dps/ $ load AAPL

Loading Daily AAPL stock with starting period 2019-05-28 for analysis.

Datetime: 2022 May 30 14:59
Timezone: America/New_York
Currency: USD
Market:   CLOSED
Company:  Apple Inc.

(🦋) /stocks/dps/ $ spos
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171170008-fafb8adc-6bcd-4050-9187-7a0674203585.png"><img alt="spos" src="https://user-images.githubusercontent.com/46355364/171170008-fafb8adc-6bcd-4050-9187-7a0674203585.png"></a>

Prolonged periods where the net short volume is above 50% are notable.

````
(🦋) /stocks/dps/ $ psi
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171170143-9f9f6f93-4068-43e1-a8f1-71f3be029235.png"><img alt="spos" src="https://user-images.githubusercontent.com/46355364/171170143-9f9f6f93-4068-43e1-a8f1-71f3be029235.png"></a>

See the aggregate sum total of fail-to-delivers, with the historical price, with the `ftd` command.

````
(🦋) /stocks/dps/ $ ftd -s 2020-05-30
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171170293-c8ea1a43-d9e1-4684-8f7c-fc4e8978d3f9.png"><img alt="ftd" src="https://user-images.githubusercontent.com/46355364/171170293-c8ea1a43-d9e1-4684-8f7c-fc4e8978d3f9.png"></a>

The data from `dpotc`, statistics for individual NMS tickers, shows weekly OTC and ATS trade volume with the average lot size, which is reported on a lagging schedule.

````
(🦋) /stocks/dps/ $ dpotc
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171170366-234aea6b-fe0d-4735-8942-4a672d0683ef.png"><img alt="dpotc" src="https://user-images.githubusercontent.com/46355364/171170366-234aea6b-fe0d-4735-8942-4a672d0683ef.png"></a>

Run a live demo of these features by entering `exe routines/darkpool_demo.openbb` into the Terminal from the home screen.

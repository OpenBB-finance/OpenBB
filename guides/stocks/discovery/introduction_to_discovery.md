---
title: Introduction to the Stocks Discovery Menu
keywords: "stocks, discovery, disc, menu, submenu, pipo, fipo, gainers, losers, ugs, gtech, active, ulc, asc, ford, arkord, upcoming, trending, cnews, lowfloat, hotpenny, rtat, divcal, dividends, short, trending, news, meme"
date: "2022-05-30"
type: guides
status: publish
excerpt: "Introducing the Discovery submenu, within the Stocks menu. This guide will empower the user to get the most out of this set of features." 
geekdocCollapseSection: true
---
<h1>Introduction to the Stocks Discovery Menu</h1>

`/stocks/disc/help`<br></br>
The set of features within the Stocks Discovery submenu provides tools for discovering trade setups, for following trends, and for staying up with current events. Enter the menu from the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">`Stocks`</a> menu by typing, `disc`, and pressing, `enter`. Absolute path jumping is possible from anywhere, to anywhere. For example, jumping from the Portfolio Optimization submenu to the Stocks Discovery submenu:

![Absolute path jumping to the Stocks Discovery submenu](discovery1.png)<br>

To use all commands in the Discovery menu, the following (free) API keys are required:<br>
  - <a href="https://www.quandl.com/" target="_blank">Quandl</a>
  - <a href="https://finnhub.io/" target="_blank">Finnhub</a><br>

  See the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/#accessing-other-sources-of-data-via-api-keys" target="_blank">Getting Started Guide</a> for setting API keys in the OpenBB Terminal.

<h2>How to use the Discovery Menu</h2><br>

The help dialogue, for any command, is displayed by attaching, `-h`, to the string; i.e., `divcal -h`. This menu will be one of the easiest to get comfortable with a command-line interface.  All outputs from commands in this menu are text and tables. There are no charts or images generated. Exports, where available, can be formatted as csv, json, or xlsx files. Watch this short demonstration of all features in this menu:<br>
![Discovery Menu Demonstration Video](discovery_demo.gif)<br>

<h2>Examples</h2>

The dividend calendar can show any single date.
````
(🦋) /stocks/disc/ $ divcal -d 2022-06-02 -l 25
````
![The 25 biggest dividend payments with an ex-div date of June 2, 2022](discovery_divcal1.png)

See Cathie Wood's trades and sort by different fields such as Fund, weighting, buy-only, or sell-only.

![Cathie Wood's trades](discovery_arkord.png)<br>

Check the upcoming earnings schedule using, `upcoming`

![Upcoming earnings calendar](discovery_upcoming.png)<br>

Browse the news by category from <a href="https://seekingalpha.com" target="_blank">Seeking Alpha</a> with, `cnews`

![News headlines by category](discovery_cnews.png)<br>

Back to <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">`Stocks`</a>


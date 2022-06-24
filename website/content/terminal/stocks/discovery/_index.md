---
title: Introduction to Stocks Discovery
keywords: "stocks, discovery, disc, menu, submenu, pipo, fipo, gainers, losers, ugs, gtech, active, ulc, asc, ford, arkord, upcoming, trending, cnews, lowfloat, hotpenny, rtat, divcal, dividends, short, trending, news"
date: "2022-05-30"
type: guides
status: publish
excerpt: "Introducing the Discovery menu, within the Stocks menu. This guide will empower the user to get the most
out of this set of features." 
geekdocCollapseSection: true
---
The set of features within the Stocks Discovery submenu provides tools for discovering trade setups, for following trends, and for staying up with current events. Enter the menu from the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">stocks</a> menu by typing, `disc`, and pressing, `ENTER` (⏎). Absolute path jumping is possible from anywhere, to anywhere. For example, jumping from the Portfolio Optimization submenu to the Stocks Discovery submenu:

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171173438-0bc7569e-1627-41a6-b9dc-5f5682fc2436.png"><img alt="Absolute path jumping to the Stocks Discovery submenu" src="https://user-images.githubusercontent.com/46355364/171173438-0bc7569e-1627-41a6-b9dc-5f5682fc2436.png"></a>

To use all commands in the Discovery menu, the following (free) API keys are required:
  - <a href="https://www.quandl.com/" target="_blank">Quandl</a>
  - <a href="https://finnhub.io/" target="_blank">Finnhub</a>
  
See the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/#accessing-other-sources-of-data-via-api-keys" target="_blank">Getting Started Guide</a> for setting API keys in the OpenBB Terminal.

## How to use

The help dialogue, for any command, is displayed by attaching, `-h`, to the string; i.e., `divcal -h`. This menu will
be one of the easiest to get comfortable with a command-line interface.  All outputs from commands in this
menu are text and tables. There are no charts or images generated. Exports, where available, can be formatted as
csv, json, or xlsx files. Watch this short demonstration of all features in this menu:

<a target="_blank" href="discovery_demo.gif"><img alt="Discovery Menu Demonstration Video" src="discovery_demo.gif"></a>

## Examples

The dividend calendar can show any single date.

````
(🦋) /stocks/disc/ $ divcal -d 2022-06-02 -l 25
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171173948-560ec4b5-0ca5-449c-b95d-d9be388dd7f3.png"><img alt="The 25 biggest dividend payments with an ex-div date of June 2, 2022" src="https://user-images.githubusercontent.com/46355364/171173948-560ec4b5-0ca5-449c-b95d-d9be388dd7f3.png"></a>

See Cathie Wood's trades and sort by different fields such as Fund, weighting, buy-only, or sell-only.

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171174166-e83d517a-cddf-47f5-a774-d1ee78f643d0.png"><img alt="Cathie Wood's trades" src="https://user-images.githubusercontent.com/46355364/171174166-e83d517a-cddf-47f5-a774-d1ee78f643d0.png"></a>

Check the upcoming earnings schedule using, `upcoming`:

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171174309-39fd9cf1-b943-42fb-a993-86a53ff8946f.png"><img alt="Upcoming earnings calendar" src="https://user-images.githubusercontent.com/46355364/171174309-39fd9cf1-b943-42fb-a993-86a53ff8946f.png"></a>

Browse the news by category from <a href="https://seekingalpha.com" target="_blank">Seeking Alpha</a> with `cnews`:

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171174415-887d78ff-1a1e-4e20-b61a-9c227bb9929d.png"><img alt="News headlines by category" src="https://user-images.githubusercontent.com/46355364/171174415-887d78ff-1a1e-4e20-b61a-9c227bb9929d.png"></a>

---
title: Introduction to the Insider Trading Menu
keywords: "Executive, director, directors, CEO, CFO, CIO, COO, DIR, sell, buy, SEC, disclosure, disclose, stats, act, lins, filter, view, set, lcb, lpsb, lit, lip, blip, blop, bclp, lis, blis, blos, blcs, topt, toppw, toppm, tipt, tippw, tippm, tist, tispw, tispm, openinsider, finviz, business, stocks, options"
date: "2022-06-10"
type: guides
status: publish
excerpt: "This guide introduces the Insider Trading submenu, within the Stocks menu, by briefly explaining the features and how to use them, showing examples in context."
geekdocCollapseSection: true
---

The Insider Trading Menu has two general purposes:
  - A stock screener for SEC Form 4 filings.
  - Researching individual companies for executive and director transactions.

Navaigate to the Insider Trading submenu from the `stocks` menu by typing `ins` and pressing `enter`. The features in this menu function only for companies registered with the SEC, that also trade in public markets.

<img width="1174" alt="Insider Trading Menu" src="https://user-images.githubusercontent.com/85772166/173204667-6be5813f-ce80-4c11-b63b-35363d8caa44.png">

<h2>How to use the Insider Trading Menu</h2>

The menu is contains three groups of functions for:
  - Setting, viewing presets for the filter, and screening.
  - Using with individual stocks.
  - Filtering all submitted SEC Form 4 records by defined metrics.

The last of these groups encompasses the majority of commands in the Insider Trading submenu. They are for scanning the entire market based on the description listed next to the command.

`lcb` - Latest cluster buys:

<img width="1177" alt="Latest Cluster Buys" src="https://user-images.githubusercontent.com/85772166/173204685-7c91e43d-5432-4532-ab07-8ce095cc3a0a.png">

With the `--export` argument attached, data from this menu can be exported as CSV, JSON, or XLSX files.

`lit` - Latest insider trades from all filings:

<img width="1177" alt="Latest Insider Trades" src="https://user-images.githubusercontent.com/85772166/173204706-08fa491d-4140-4d39-a787-325524fb5bd0.png">

`tispm` - Top insider sales from the last month:

<img width="1175" alt="Top insider sales from the last month" src="https://user-images.githubusercontent.com/85772166/173204715-626fd866-33e7-499c-9f24-c1b71e5b84fa.png">

`view` will list the available presets to use as a screener. The screener uses `.ini` files which can be modified by the user to create custom presets. Find them in the local installation folder, under: `~/OpenBB/openbb_terminal/stocks/insider/presets/`. The default preset is `whales`, which targets trades over $500K in the last two weeks. Other included presets are for scanning individual industries as a group.

The `set` command is used to select a preset. Autocomplete will assist the user and the arrow keys can be used to make a choice. Use the file `template.ini` to build a custom preset. Changes made to an existing `.ini` file will be effective the next time the `filter` command is run.

<img width="1139" alt="Set Command" src="https://user-images.githubusercontent.com/85772166/173204733-7189ea05-68e5-465d-bef9-b74861842894.png">

`filter` will screen based on the selected preset.

<img width="1175" alt="Filter Command" src="https://user-images.githubusercontent.com/85772166/173204750-e811e346-091f-4d92-93bf-f942528eef6c.png">

With a ticker loaded the `stats`, `act`, and `lins` commands are available.

<img width="1173" alt="Stats Command with RKT loaded" src="https://user-images.githubusercontent.com/85772166/173204762-1fc19a6a-99d1-44af-8034-ead70d2858c7.png">

<h2>Examples</h2>

Using the Retail-Trade preset:

<img width="1172" alt="Retail Trade Screener" src="https://user-images.githubusercontent.com/85772166/173204772-5cc8770e-801f-4a02-8b12-94c4bed948da.png">

Using the Guided-Missiles preset:

<img width="1175" alt="Guided Missiles Screener" src="https://user-images.githubusercontent.com/85772166/173204809-c89c346c-f1a9-4202-919e-16a2641abe73.png">

`act` shows recent trading activity plotted with the price:

![Insider trading activity and Price of TSLA](https://user-images.githubusercontent.com/85772166/173204788-8684f30e-3625-423d-a61d-90b5edcd62df.png)

The latest purchases from insiders of penny stock companies:

<img width="1173" alt="Last Penny Stock Insider Purchases" src="https://user-images.githubusercontent.com/85772166/173204831-a859ce15-13aa-4f1c-afa9-88a3086ef37a.png">

Run `exe insider_demo.openbb`, from the Main Menu, to play a demonstration of the features in the OpenBB Terminal.

Back to: <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/">Introduction to Stocks</a>

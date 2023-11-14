---
title: Behavioural Analysis
description: The page introduces the Behavioural Analysis sub-menu, within the Stocks menu, of the OpenBB Terminal.
keywords:
- Behavioural Analysis
- public sentiment
- momentum trading strategies
- stocks
- companies
- reddit
- twitter
- stocktwits
- x
- google
- API key
- /r/wallstreetbets
- social sentiment
- deep learning algorithms
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Behavioural Analysis - Stocks - Menus | OpenBB Terminal Docs" />

The Behavioural Analysis menu offers the user tools for gauging the overall public sentiment of a company online. The complexity of the tools range from message board scrapers to deep learning algorithms for financial analysis and prediction. Sentiment is particularly useful for momentum trading strategies, discovery, and general fundamental research. 

## Usage

Navigate into the menu from the Stocks menu by entering, `ba`. Or, by using the absolute path from anywhere in the Terminal:

```console
/stocks/ba
```

![Screenshot 2023-10-31 at 1 50 04 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/5946bc28-95a8-4402-a546-68be140aa025)

### Trending

The `trending` command gets the list of trending tickers, according to Stocktwits.

```console
/stocks/ba/trending
```

| Ticker   |   Watchlist Count | Name                                            |
|:---------|------------------:|:------------------------------------------------|
| AMD      |            468973 | Advanced Micro Devices Inc.                     |
| NVDA     |            447556 | NVIDIA Corp                                     |
| XRP.X    |            158654 | Ripple                                          |
| CHK      |             61074 | Chesapeake Energy Corp. - Ordinary Shares - New |
| PINS     |             44549 | PINTEREST INC                                   |
| CRSP     |             34881 | CRISPR Therapeutics AG                          |
| CAT      |             29787 | Caterpillar Inc.                                |
| FSLR     |             28779 | First Solar Inc                                 |
| CVS      |             26361 | CVS Health Corp                                 |
| SAVE     |             24589 | Spirit Airlines Inc                             |
| SRPT     |             18634 | Sarepta Therapeutics Inc                        |
| Z        |             18152 | Zillow Group Inc                                |
| BUD      |             13161 | Anheuser-Busch InBev                            |
| MTCH     |             12638 | Match Group Inc.                                |
| UEC      |             12473 | Uranium Energy Corp                             |
| CZR      |             10943 | Caesars Entertainment Inc                       |
| CCJ      |             10108 | Cameco Corp.                                    |
| ANET     |              9235 | Arista Networks Inc                             |
| CELH     |              9012 | Celsius Holdings Inc                            |
| LTHM     |              8206 | Livent Corp                                     |
| MPC      |              7307 | Marathon Petroleum Corp                         |
| PAYC     |              5425 | Paycom Software Inc                             |
| ZI       |              5061 | ZoomInfo Technologies Inc.                      |
| SPRC     |              3789 | SCISPARC LTD                                    |
| ELF      |              3658 | e.l.f. Beauty Inc                               |
| XDC.X    |              3073 | XinFin Network                                  |
| KRL.X    |              2385 | Kryll                                           |
| FRSH     |              1935 | Freshworks Inc                                  |
| MTZ      |              1544 | Mastec Inc.                                     |
| VERV     |              1054 | Verve Therapeutics Inc                          |

### Bullbear

`bullbear` gives a fast sentiment synopsis from the most recent Stocktwits posts.

```console
/stocks/ba/load crsp/bullbear
```

```console
Watchlist count: 34881

Last 15 sentiment messages:
Bullish: 80.0%
Bearish: 20.0%
```

```console
/stocks/ba/load amd/bullbear
```

```console
Watchlist count: 468973

Last 12 sentiment messages:
Bullish: 50.0%
Bearish: 50.0%
```

### Redditsent

`redditsent` will crawl through posts related to the ticker and give it a score based on how polarizing the message is.

![Screenshot 2023-10-31 at 2 28 52 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/71e6a3c9-ece8-45a4-afca-150211ae7c43)

### Queries

The `queries` command shows the terms people are including when searching for the company on Google.

```console
/stocks/ba/load amd/queries
```

| query       | value   |
|:------------|:--------|
| amd ryzen   | 100%    |
| amd radeon  | 67%     |
| radeon      | 62%     |
| amd stock   | 52%     |
| amd ryzen 5 | 47%     |
| intel       | 46%     |
| amd ryzen 7 | 25%     |
| nvidia      | 23%     |
| amd driver  | 22%     |
| amd cpu     | 21%     |

```console
/stocks/ba/load intc/queries
```

| query            | value   |
|:-----------------|:--------|
| stock intc       | 100%    |
| intc price       | 36%     |
| stock price intc | 32%     |
| amd              | 15%     |
| amd stock        | 12%     |
| aapl             | 9%      |
| msft             | 8%      |
| intc share       | 7%      |
| nvda             | 7%      |
| tsla             | 7%      |

---
title: Sector & Industry Analysis (SIA)
keywords: [sector, industry, analysis, stocks, openbb terminal]
description: A sector analysis is a study of the economic and financial state and prospects of a certain economic sector. An investor can use sector analysis to make a prediction about how well companies in the sector will perform. Investors that specialize in a specific sector or who utilize a top-down or sector rotation approach to investing generally use sector analysis.
---
A sector analysis is a study of the economic and financial state and prospects of a certain economic sector. An investor can use sector analysis to make a prediction about how well companies in the sector will perform. Investors that specialize in a specific sector or who utilize a top-down or sector rotation approach to investing generally use sector analysis.

The most promising sectors are chosen first under the top-down strategy, and then the investor evaluates stocks within that sector to choose which ones will be purchased. Investing in specific equities or using sector-based exchange-traded funds can be used to implement a sector rotation strategy (ETFs).

## How to use

When you have loaded in a ticker, the menu automatically finds the corresponding industry, sector, country and market cap.

<img width="800" alt="image" src="https://user-images.githubusercontent.com/46355364/218983925-ccdc19dd-a96c-46a8-b148-ff2aa17e0be0.png"></img>

Based on this information, you can get insights in a variety of datapoints, for example with `cps` you are able to see the companies based per sector and market cap:

![CPS](https://user-images.githubusercontent.com/46355364/218984262-a5b5e8e7-ddd3-4b07-80b2-40c9e760f102.png)

Whenever you want to adjust the parameters you can do so with `industry`, `sector`, `country` and `mktcap`. These have multiple options depending on your selection as you will see that the options expand when you use `clear` followed by a param, e.g. `clear --param mktcap` which removes the market cap value:

```
│ Industry          : Auto Manufacturers                                                                                                                                                  │
│ Sector            : Consumer Cyclical                                                                                                                                                   │
│ Country           : United States                                                                                                                                                       │
│ Market Cap        :                                                                                                                                                                     │
│ Exclude Exchanges : True                                                                                                                                                                │
│ Period            : Annual
```

This means that if you now obtain data for this selection, you get data for all companies in this combination of industry, sector and country instead of just the ones that have a Mega Cap. In the case of our loaded ticker, TSLA, it was quite clear that with this parameter only a few companies would show up whereas if we now use `metric --metric roa`, displaying the Return on Assets (RoA) gives a lot more insights.

![Metric ROA](https://user-images.githubusercontent.com/46355364/218985528-755a6c27-fa41-4c62-b115-d38a1e0c2a5d.png)

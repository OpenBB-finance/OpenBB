---
title: performance
description: This page outlines the parameters and usage for retrieving performance
  data of various stocks, using predefined filter presets. It provides different ways
  of sorting and limiting the data output.
keywords:
- performance data
- filter presets
- stock analysis
- top performers
- overbought stocks
- oversold stocks
- stock sorting
- stock scanning
- stock volatility
- stock volume
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/screener/performance - Reference | OpenBB Terminal Docs" />

Prints performance data of the companies that meet the pre-set filtering.

### Usage

```python
performance [-p Desired preset.] [-l LIMIT] [-r] [-s SORTBY]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| preset | Filter presets | top_gainers | True | template, oversold_under_5dol, potential_reversals, top_performers_all, death_cross, unusual_volume, news_scanner, cheap_bottom_dividend, cheap_dividend, top_performers_healthcare, bull_runs_over_10pct, value_stocks, golden_cross, growth_stocks, channel_up_and_low_debt_and_sma_50and200, buffett_like, continued_momentum_scan, analyst_strong_buy, under_15dol_stocks, 5pct_above_low, cheap_oversold, weak_support_and_top_performers, undervalue, oversold_under_3dol, top_performers_tech, rosenwald_gtfo, recent_growth_and_support, heavy_inst_ins, modified_neff, simplistic_momentum_scanner_under_7dol, golden_cross_penny, break_out_stocks, high_vol_and_low_debt, stocks_strong_support_levels, sexy_year, short_squeeze_scan, oversold, rosenwald, modified_dreman, top_gainers, top_losers, new_high, new_low, most_volatile, most_active, overbought, downgrades, upgrades, earnings_before, earnings_after, recent_insider_buying, recent_insider_selling, major_news, horizontal_sr, tl_resistance, tl_support, wedge_up, wedge_down, wedge, triangle_ascending, triangle_descending, channel_up, channel_down, channel, double_top, double_bottom, multiple_top, multiple_bottom, head_shoulders, head_shoulders_inverse |
| limit | Limit of stocks to print | 10 | True | None |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| sort | Sort elements of the table. | Ticker | True | ticker, perfweek, perfmonth, perfquart, perfhalf, perfyear, perfytd, volatilityw, volatilitym, recom, avgvolume, relvolume, price, change, volume |

---

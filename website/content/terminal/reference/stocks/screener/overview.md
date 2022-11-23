---
title: overview
description: OpenBB Terminal Function
---

# overview

Prints overview data of the companies that meet the pre-set filtering.

### Usage

```python
usage: overview [-p Desired preset.] [-l LIMIT] [-r] [-s SORT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| preset | Filter presets | top_gainers | True | cheap_dividend, top_performers_all, top_performers_healthcare, potential_reversals, simplistic_momentum_scanner_under_7dol, stocks_strong_support_levels, weak_support_and_top_performers, unusual_volume, bull_runs_over_10pct, modified_dreman, template, cheap_bottom_dividend, break_out_stocks, heavy_inst_ins, golden_cross, growth_stocks, value_stocks, sexy_year, 5pct_above_low, buffett_like, death_cross, golden_cross_penny, oversold_under_3dol, short_squeeze_scan, cheap_oversold, continued_momentum_scan, top_performers_tech, analyst_strong_buy, oversold_under_5dol, modified_neff, oversold, rosenwald_gtfo, news_scanner, recent_growth_and_support, rosenwald, undervalue, high_vol_and_low_debt, under_15dol_stocks, channel_up_and_low_debt_and_sma_50and200, top_gainers, top_losers, new_high, new_low, most_volatile, most_active, overbought, downgrades, upgrades, earnings_before, earnings_after, recent_insider_buying, recent_insider_selling, major_news, horizontal_sr, tl_resistance, tl_support, wedge_up, wedge_down, wedge, triangle_ascending, triangle_descending, channel_up, channel_down, channel, double_top, double_bottom, multiple_top, multiple_bottom, head_shoulders, head_shoulders_inverse |
| limit | Limit of stocks to print | 10 | True | None |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| sort | Sort elements of the table. | Ticker | True | ticker, company, sector, industry, country, marketcap, p/e, price, change, volume |
---


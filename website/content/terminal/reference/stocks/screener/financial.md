---
title: financial
description: OpenBB Terminal Function
---

# financial

Prints financial data of the companies that meet the pre-set filtering.

### Usage

```python
usage: financial [-p Desired preset.] [-l LIMIT] [-r] [-s SORT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| preset | Filter presets | top_gainers | True | weak_support_and_top_performers, buffett_like, top_performers_healthcare, modified_dreman, news_scanner, high_vol_and_low_debt, channel_up_and_low_debt_and_sma_50and200, top_performers_all, bull_runs_over_10pct, value_stocks, oversold_under_5dol, heavy_inst_ins, growth_stocks, unusual_volume, break_out_stocks, oversold_under_3dol, analyst_strong_buy, death_cross, cheap_dividend, short_squeeze_scan, stocks_strong_support_levels, modified_neff, oversold, under_15dol_stocks, potential_reversals, sexy_year, undervalue, template, continued_momentum_scan, cheap_bottom_dividend, top_performers_tech, cheap_oversold, simplistic_momentum_scanner_under_7dol, golden_cross_penny, 5pct_above_low, rosenwald_gtfo, golden_cross, recent_growth_and_support, rosenwald, top_gainers, top_losers, new_high, new_low, most_volatile, most_active, overbought, downgrades, upgrades, earnings_before, earnings_after, recent_insider_buying, recent_insider_selling, major_news, horizontal_sr, tl_resistance, tl_support, wedge_up, wedge_down, wedge, triangle_ascending, triangle_descending, channel_up, channel_down, channel, double_top, double_bottom, multiple_top, multiple_bottom, head_shoulders, head_shoulders_inverse |
| limit | Limit of stocks to print | 10 | True | None |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| sort | Sort elements of the table. | Ticker | True | ticker, marketcap, dividend, roa, roe, roi, currr, quickr, ltdebt/eq, debt/eq, grossm, operm, profitm, earnings, price, change, volume |
---


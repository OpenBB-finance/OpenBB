---
title: technical
description: OpenBB Terminal Function
---

# technical

Prints technical data of the companies that meet the pre-set filtering.

### Usage

```python
usage: technical [-p Desired preset.] [-l LIMIT] [-r]
                 [-s {ticker,beta,atr,sma20,sma50,sma200,52whigh,52wlow,rsi,price,change,fromopen,gap,volume}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| preset | Filter presets | top_gainers | True | sexy_year, analyst_strong_buy, 5pct_above_low, potential_reversals, oversold_under_3dol, top_performers_healthcare, heavy_inst_ins, continued_momentum_scan, recent_growth_and_support, oversold, break_out_stocks, news_scanner, simplistic_momentum_scanner_under_7dol, short_squeeze_scan, value_stocks, under_15dol_stocks, template, cheap_bottom_dividend, weak_support_and_top_performers, high_vol_and_low_debt, golden_cross, oversold_under_5dol, unusual_volume, cheap_oversold, top_performers_tech, golden_cross_penny, stocks_strong_support_levels, top_performers_all, rosenwald_gtfo, rosenwald, bull_runs_over_10pct, modified_dreman, cheap_dividend, death_cross, modified_neff, growth_stocks, channel_up_and_low_debt_and_sma_50and200, buffett_like, undervalue, top_gainers, top_losers, new_high, new_low, most_volatile, most_active, overbought, downgrades, upgrades, earnings_before, earnings_after, recent_insider_buying, recent_insider_selling, major_news, horizontal_sr, tl_resistance, tl_support, wedge_up, wedge_down, wedge, triangle_ascending, triangle_descending, channel_up, channel_down, channel, double_top, double_bottom, multiple_top, multiple_bottom, head_shoulders, head_shoulders_inverse |
| limit | Limit of stocks to print | 10 | True | None |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| sort | Sort elements of the table. | Ticker | True | ticker, beta, atr, sma20, sma50, sma200, 52whigh, 52wlow, rsi, price, change, fromopen, gap, volume |
---


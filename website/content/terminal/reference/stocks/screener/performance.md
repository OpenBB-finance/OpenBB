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

<HeadTitle title="stocks /screener/performance - Reference | OpenBB Terminal Docs" />

Prints performance data of the companies that meet the pre-set filtering.

### Usage

```python wordwrap
performance [-p Desired preset.] [-l LIMIT] [-r] [-s SORTBY]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| preset | -p  --preset | Filter presets | top_gainers | True | 5pct_above_low, analyst_strong_buy, break_out_stocks, buffett_like, bull_runs_over_10pct, channel_up_and_low_debt_and_sma_50and200, cheap_bottom_dividend, cheap_dividend, cheap_oversold, continued_momentum_scan, death_cross, djia_components, golden_cross, golden_cross_penny, growth_stocks, heavy_inst_ins, high_vol_and_low_debt, modified_dreman, modified_neff, news_scanner, oversold, oversold_under_3dol, oversold_under_5dol, potential_reversals, recent_growth_and_support, rosenwald, rosenwald_gtfo, sdk_guide_preset, sexy_year, short_squeeze_scan, simplistic_momentum_scanner_under_7dol, sp500_basic_materials_sector, sp500_communication_services_sector, sp500_consumer_cyclical_sector, sp500_consumer_defensive_sector, sp500_energy_sector, sp500_financial_sector, sp500_healthcare_sector, sp500_industrials_sector, sp500_real_estate_sector, sp500_technology_sector, sp500_utilities_sector, stocks_strong_support_levels, top_performers_all, top_performers_healthcare, top_performers_tech, undervalue, under_15dol_stocks, unusual_volume, value_stocks, weak_support_and_top_performers, top_gainers, top_losers, new_high, new_low, most_volatile, most_active, overbought, downgrades, upgrades, earnings_before, earnings_after, recent_insider_buying, recent_insider_selling, major_news, horizontal_sr, tl_resistance, tl_support, wedge_up, wedge_down, wedge, triangle_ascending, triangle_descending, channel_up, channel_down, channel, double_top, double_bottom, multiple_top, multiple_bottom, head_shoulders, head_shoulders_inverse |
| limit | -l  --limit | Limit of stocks to print | 0 | True | None |
| reverse | -r  --reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| sort | -s  --sort | Sort elements of the table. | ytd | True | ticker, 1w, 1m, 3m, 6m, 1y, ytd, 1wvolatility, 1mvolatility, recom, avgvolume, relvolume, price, change, volume |

---

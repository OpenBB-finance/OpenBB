```
usage: valuation
                 [-p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}]
                 [-l LIMIT] [-a]
                 [-s {Ticker,Market Cap,P/E,Fwd P/E,PEG,P/S,P/B,P/C,P/FCF,EPS this Y,EPS next Y,EPS past 5Y,EPS next 5Y,Sales past 5Y,Price,Change,Volume} [{Ticker,Market Cap,P/E,Fwd P/E,PEG,P/S,P/B,P/C,P/FCF,EPS this Y,EPS next Y,EPS past 5Y,EPS next 5Y,Sales past 5Y,Price,Change,Volume} ...]]
                 [-h] [--export {csv,json,xlsx}]
```

Prints valuation data of the companies that meet the pre-set filtering. [Source: Finviz]

```
optional arguments:
  -p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}, --preset {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}
                        Filter presets
  -l LIMIT, --limit LIMIT
                        Limit of stocks to print
  -a, --ascend          Set order to Ascend, the default is Descend
  -s {Ticker,Market Cap,P/E,Fwd P/E,PEG,P/S,P/B,P/C,P/FCF,EPS this Y,EPS next Y,EPS past 5Y,EPS next 5Y,Sales past 5Y,Price,Change,Volume} [{Ticker,Market Cap,P/E,Fwd P/E,PEG,P/S,P/B,P/C,P/FCF,EPS this Y,EPS next Y,EPS past 5Y,EPS next 5Y,Sales past 5Y,Price,Change,Volume} ...], --sort {Ticker,Market Cap,P/E,Fwd P/E,PEG,P/S,P/B,P/C,P/FCF,EPS this Y,EPS next Y,EPS past 5Y,EPS next 5Y,Sales past 5Y,Price,Change,Volume} [{Ticker,Market Cap,P/E,Fwd P/E,PEG,P/S,P/B,P/C,P/FCF,EPS this Y,EPS next Y,EPS past 5Y,EPS next 5Y,Sales past 5Y,Price,Change,Volume} ...]
                        Sort elements of the table.
  -h, --help            show this help message
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx
```

```
2022 Feb 14, 08:55 (✨) /stocks/scr/ $ valuation -p potential_reversals
                                                                                       Finzin Screener
┌────────┬────────────────┬────────┬─────────┬───────┬───────┬───────┬───────┬────────┬────────────┬────────────┬─────────────┬─────────────┬───────────────┬────────┬────────┬─────────────┐
│ Ticker │ Market Cap     │ P/E    │ Fwd P/E │ PEG   │ P/S   │ P/B   │ P/C   │ P/FCF  │ EPS this Y │ EPS next Y │ EPS past 5Y │ EPS next 5Y │ Sales past 5Y │ Price  │ Change │ Volume      │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ ZYNE   │ 117100000.00   │        │         │       │       │ 1.35  │ 1.55  │        │ -0.27      │ -0.04      │ 0.08        │             │               │ 2.65   │ -0.07  │ 2010373.00  │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ ZS     │ 39800000000.00 │        │ 294.82  │       │ 52.30 │ 71.65 │ 25.12 │ 202.95 │ -1.17      │ 0.77       │ -0.44       │ 0.45        │ 0.53          │ 273.00 │ -0.04  │ 2014963.00  │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ ZNGA   │ 10270000000.00 │        │ 19.61   │       │ 3.67  │ 3.34  │ 7.67  │ 33.69  │ -0.03      │ 0.20       │ -0.26       │ 0.18        │ 0.21          │ 9.16   │ -0.00  │ 22552624.00 │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ ZION   │ 11600000000.00 │ 11.00  │ 12.68   │       │ 5.08  │ 1.60  │ 0.89  │ 67.04  │ -0.27      │ 0.16       │ 0.20        │             │ 0.05          │ 73.22  │ -0.01  │ 1226228.00  │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ ZI     │ 22650000000.00 │ 818.97 │ 81.18   │ 19.45 │ 34.08 │ 8.21  │ 97.09 │ 82.61  │ 0.53       │ 0.33       │             │ 0.42        │               │ 55.69  │ -0.02  │ 3612070.00  │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ ZGNX   │ 1470000000.00  │        │         │       │ 23.17 │ 6.52  │ 4.30  │        │ 0.60       │ 0.31       │ -0.15       │             │ -0.13         │ 26.15  │ -0.01  │ 1507686.00  │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ ZG     │ 12310000000.00 │        │ 19.08   │       │ 2.44  │ 2.57  │ 3.94  │        │ -1.92      │ 0.61       │ -0.12       │             │ 0.57          │ 53.92  │ 0.13   │ 8236415.00  │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ Z      │ 10370000000.00 │        │ 71.95   │       │ 2.05  │ 2.45  │       │        │ -3.43      │ 1.72       │             │             │               │ 55.40  │ 0.14   │ 50184008.00 │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ YMAB   │ 285860000.00   │        │         │       │ 6.21  │ 1.70  │ 1.33  │        │ -0.29      │ 0.12       │             │             │               │ 8.25   │ 0.26   │ 12286763.00 │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ YELL   │ 538640000.00   │        │ 9.31    │       │ 0.11  │       │ 1.73  │        │ -0.68      │ 0.24       │ -0.40       │             │ 0.02          │ 9.96   │ -0.05  │ 505353.00   │
└────────┴────────────────┴────────┴─────────┴───────┴───────┴───────┴───────┴────────┴────────────┴────────────┴─────────────┴─────────────┴───────────────┴────────┴────────┴─────────────┘

2022 Feb 14, 08:56 (✨) /stocks/scr/ $ valuation -p major_news
                                                                                       Finzin Screener
┌────────┬────────────────┬────────┬─────────┬───────┬───────┬───────┬───────┬────────┬────────────┬────────────┬─────────────┬─────────────┬───────────────┬────────┬────────┬─────────────┐
│ Ticker │ Market Cap     │ P/E    │ Fwd P/E │ PEG   │ P/S   │ P/B   │ P/C   │ P/FCF  │ EPS this Y │ EPS next Y │ EPS past 5Y │ EPS next 5Y │ Sales past 5Y │ Price  │ Change │ Volume      │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ ZYNE   │ 117100000.00   │        │         │       │       │ 1.35  │ 1.55  │        │ -0.27      │ -0.04      │ 0.08        │             │               │ 2.65   │ -0.07  │ 2010373.00  │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ ZS     │ 39800000000.00 │        │ 294.82  │       │ 52.30 │ 71.65 │ 25.12 │ 202.95 │ -1.17      │ 0.77       │ -0.44       │ 0.45        │ 0.53          │ 273.00 │ -0.04  │ 2014963.00  │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ ZNGA   │ 10270000000.00 │        │ 19.61   │       │ 3.67  │ 3.34  │ 7.67  │ 33.69  │ -0.03      │ 0.20       │ -0.26       │ 0.18        │ 0.21          │ 9.16   │ -0.00  │ 22552624.00 │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ ZION   │ 11600000000.00 │ 11.00  │ 12.68   │       │ 5.08  │ 1.60  │ 0.89  │ 67.04  │ -0.27      │ 0.16       │ 0.20        │             │ 0.05          │ 73.22  │ -0.01  │ 1226228.00  │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ ZI     │ 22650000000.00 │ 818.97 │ 81.18   │ 19.45 │ 34.08 │ 8.21  │ 97.09 │ 82.61  │ 0.53       │ 0.33       │             │ 0.42        │               │ 55.69  │ -0.02  │ 3612070.00  │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ ZGNX   │ 1470000000.00  │        │         │       │ 23.17 │ 6.52  │ 4.30  │        │ 0.60       │ 0.31       │ -0.15       │             │ -0.13         │ 26.15  │ -0.01  │ 1507686.00  │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ ZG     │ 12310000000.00 │        │ 19.08   │       │ 2.44  │ 2.57  │ 3.94  │        │ -1.92      │ 0.61       │ -0.12       │             │ 0.57          │ 53.92  │ 0.13   │ 8236415.00  │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ Z      │ 10370000000.00 │        │ 71.95   │       │ 2.05  │ 2.45  │       │        │ -3.43      │ 1.72       │             │             │               │ 55.40  │ 0.14   │ 50184008.00 │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ YMAB   │ 285860000.00   │        │         │       │ 6.21  │ 1.70  │ 1.33  │        │ -0.29      │ 0.12       │             │             │               │ 8.25   │ 0.26   │ 12286763.00 │
├────────┼────────────────┼────────┼─────────┼───────┼───────┼───────┼───────┼────────┼────────────┼────────────┼─────────────┼─────────────┼───────────────┼────────┼────────┼─────────────┤
│ YELL   │ 538640000.00   │        │ 9.31    │       │ 0.11  │       │ 1.73  │        │ -0.68      │ 0.24       │ -0.40       │             │ 0.02          │ 9.96   │ -0.05  │ 505353.00   │
└────────┴────────────────┴────────┴─────────┴───────┴───────┴───────┴───────┴────────┴────────────┴────────────┴─────────────┴─────────────┴───────────────┴────────┴────────┴─────────────┘
```

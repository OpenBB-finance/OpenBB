```
usage: technical
                 [-p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}]
                 [-l LIMIT] [-a] [-s {Ticker,Beta,ATR,SMA20,SMA50,SMA200,52W High,52W Low,RSI,Price,Change,from Open,Gap,Volume} [{Ticker,Beta,ATR,SMA20,SMA50,SMA200,52W High,52W Low,RSI,Price,Change,from Open,Gap,Volume} ...]] [-h]
                 [--export {csv,json,xlsx}]
```

Prints technical data of the companies that meet the pre-set filtering. [Source: Finviz]

```
optional arguments:
  -p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}, --preset {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}
                        Filter presets
  -l LIMIT, --limit LIMIT
                        Limit of stocks to print
  -a, --ascend          Set order to Ascend, the default is Descend
  -s {Ticker,Beta,ATR,SMA20,SMA50,SMA200,52W High,52W Low,RSI,Price,Change,from Open,Gap,Volume} [{Ticker,Beta,ATR,SMA20,SMA50,SMA200,52W High,52W Low,RSI,Price,Change,from Open,Gap,Volume} ...], --sort {Ticker,Beta,ATR,SMA20,SMA50,SMA200,52W High,52W Low,RSI,Price,Change,from Open,Gap,Volume} [{Ticker,Beta,ATR,SMA20,SMA50,SMA200,52W High,52W Low,RSI,Price,Change,from Open,Gap,Volume} ...]
                        Sort elements of the table.
  -h, --help            show this help message
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx
```

```
2022 Feb 14, 08:53 (✨) /stocks/scr/ $ technical -p cheap_bottom_dividend
                                                          Finzin Screener
┌────────┬───────┬───────┬───────┬───────┬────────┬──────────┬─────────┬───────┬────────┬────────┬───────────┬───────┬─────────────┐
│ Ticker │ Beta  │ ATR   │ SMA20 │ SMA50 │ SMA200 │ 52W High │ 52W Low │ RSI   │ Price  │ Change │ from Open │ Gap   │ Volume      │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ ZYNE   │ 2.12  │ 0.17  │ 0.03  │ -0.08 │ -0.35  │ -0.67    │ 0.20    │ 46.60 │ 2.65   │ -0.07  │ -0.07     │ 0.00  │ 2010373.00  │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ ZS     │ 0.97  │ 16.67 │ 0.08  │ -0.03 │ 0.05   │ -0.27    │ 0.74    │ 52.90 │ 273.00 │ -0.04  │ -0.04     │ 0.00  │ 2014963.00  │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ ZNGA   │ -0.09 │ 0.31  │ 0.02  │ 0.22  │ 0.06   │ -0.26    │ 0.64    │ 70.17 │ 9.16   │ -0.00  │ 0.00      │ -0.00 │ 22552624.00 │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ ZION   │ 1.31  │ 2.26  │ 0.07  │ 0.11  │ 0.22   │ -0.03    │ 0.56    │ 64.14 │ 73.22  │ -0.01  │ -0.00     │ -0.01 │ 1226228.00  │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ ZI     │       │ 3.69  │ 0.10  │ -0.02 │ -0.04  │ -0.30    │ 0.47    │ 53.94 │ 55.69  │ -0.02  │ -0.03     │ 0.00  │ 3612070.00  │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ ZGNX   │ 0.90  │ 0.66  │ 0.07  │ 0.40  │ 0.56   │ -0.02    │ 1.37    │ 78.94 │ 26.15  │ -0.01  │ -0.00     │ -0.00 │ 1507686.00  │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ ZG     │ 1.54  │ 3.19  │ 0.08  │ -0.03 │ -0.39  │ -0.75    │ 0.22    │ 55.39 │ 53.92  │ 0.13   │ -0.01     │ 0.14  │ 8236415.00  │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ Z      │       │ 3.27  │ 0.09  │ -0.02 │ -0.37  │ -0.73    │ 0.24    │ 56.28 │ 55.40  │ 0.14   │ -0.01     │ 0.15  │ 50184008.00 │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ YMAB   │ 1.28  │ 1.16  │ -0.13 │ -0.39 │ -0.68  │ -0.84    │ 0.27    │ 37.67 │ 8.25   │ 0.26   │ 0.25      │ 0.01  │ 12286763.00 │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ YELL   │ 3.10  │ 0.81  │ -0.05 │ -0.14 │ 0.19   │ -0.35    │ 1.05    │ 43.45 │ 9.96   │ -0.05  │ -0.04     │ -0.01 │ 505353.00   │
└────────┴───────┴───────┴───────┴───────┴────────┴──────────┴─────────┴───────┴────────┴────────┴───────────┴───────┴─────────────┘

2022 Feb 14, 08:53 (✨) /stocks/scr/ $ technical -p recent_insider_selling
                                                          Finzin Screener
┌────────┬───────┬───────┬───────┬───────┬────────┬──────────┬─────────┬───────┬────────┬────────┬───────────┬───────┬─────────────┐
│ Ticker │ Beta  │ ATR   │ SMA20 │ SMA50 │ SMA200 │ 52W High │ 52W Low │ RSI   │ Price  │ Change │ from Open │ Gap   │ Volume      │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ ZYNE   │ 2.12  │ 0.17  │ 0.03  │ -0.08 │ -0.35  │ -0.67    │ 0.20    │ 46.60 │ 2.65   │ -0.07  │ -0.07     │ 0.00  │ 2010373.00  │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ ZS     │ 0.97  │ 16.67 │ 0.08  │ -0.03 │ 0.05   │ -0.27    │ 0.74    │ 52.90 │ 273.00 │ -0.04  │ -0.04     │ 0.00  │ 2014963.00  │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ ZNGA   │ -0.09 │ 0.31  │ 0.02  │ 0.22  │ 0.06   │ -0.26    │ 0.64    │ 70.17 │ 9.16   │ -0.00  │ 0.00      │ -0.00 │ 22552624.00 │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ ZION   │ 1.31  │ 2.26  │ 0.07  │ 0.11  │ 0.22   │ -0.03    │ 0.56    │ 64.14 │ 73.22  │ -0.01  │ -0.00     │ -0.01 │ 1226228.00  │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ ZI     │       │ 3.69  │ 0.10  │ -0.02 │ -0.04  │ -0.30    │ 0.47    │ 53.94 │ 55.69  │ -0.02  │ -0.03     │ 0.00  │ 3612070.00  │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ ZGNX   │ 0.90  │ 0.66  │ 0.07  │ 0.40  │ 0.56   │ -0.02    │ 1.37    │ 78.94 │ 26.15  │ -0.01  │ -0.00     │ -0.00 │ 1507686.00  │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ ZG     │ 1.54  │ 3.19  │ 0.08  │ -0.03 │ -0.39  │ -0.75    │ 0.22    │ 55.39 │ 53.92  │ 0.13   │ -0.01     │ 0.14  │ 8236415.00  │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ Z      │       │ 3.27  │ 0.09  │ -0.02 │ -0.37  │ -0.73    │ 0.24    │ 56.28 │ 55.40  │ 0.14   │ -0.01     │ 0.15  │ 50184008.00 │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ YMAB   │ 1.28  │ 1.16  │ -0.13 │ -0.39 │ -0.68  │ -0.84    │ 0.27    │ 37.67 │ 8.25   │ 0.26   │ 0.25      │ 0.01  │ 12286763.00 │
├────────┼───────┼───────┼───────┼───────┼────────┼──────────┼─────────┼───────┼────────┼────────┼───────────┼───────┼─────────────┤
│ YELL   │ 3.10  │ 0.81  │ -0.05 │ -0.14 │ 0.19   │ -0.35    │ 1.05    │ 43.45 │ 9.96   │ -0.05  │ -0.04     │ -0.01 │ 505353.00   │
└────────┴───────┴───────┴───────┴───────┴────────┴──────────┴─────────┴───────┴────────┴────────┴───────────┴───────┴─────────────┘
```

```
usage: performance
                   [-p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}]
                   [-l LIMIT] [-a]
                   [-s {Ticker,Perf Week,Perf Month,Perf Quart,Perf Half,Perf Year,Perf YTD,Volatility W,Volatility M,Recom,Avg Volume,Rel Volume,Price,Change,Volume} [{Ticker,Perf Week,Perf Month,Perf Quart,Perf Half,Perf Year,Perf YTD,Volatility W,Volatility M,Recom,Avg Volume,Rel Volume,Price,Change,Volume} ...]]
                   [-h] [--export {csv,json,xlsx}]
```

Prints performance data of the companies that meet the pre-set filtering. [Source: Finviz]

```
optional arguments:
  -p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}, --preset {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}
                        Filter presets
  -l LIMIT, --limit LIMIT
                        Limit of stocks to print
  -a, --ascend          Set order to Ascend, the default is Descend
  -s {Ticker,Perf Week,Perf Month,Perf Quart,Perf Half,Perf Year,Perf YTD,Volatility W,Volatility M,Recom,Avg Volume,Rel Volume,Price,Change,Volume} [{Ticker,Perf Week,Perf Month,Perf Quart,Perf Half,Perf Year,Perf YTD,Volatility W,Volatility M,Recom,Avg Volume,Rel Volume,Price,Change,Volume} ...], --sort {Ticker,Perf Week,Perf Month,Perf Quart,Perf Half,Perf Year,Perf YTD,Volatility W,Volatility M,Recom,Avg Volume,Rel Volume,Price,Change,Volume} [{Ticker,Perf Week,Perf Month,Perf Quart,Perf Half,Perf Year,Perf YTD,Volatility W,Volatility M,Recom,Avg Volume,Rel Volume,Price,Change,Volume} ...]
                        Sort elements of the table.
  -h, --help            show this help message
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx
```

```
2022 Feb 14, 08:44 (✨) /stocks/scr/ $ performance -p rosenwald
                                                                                   Finzin Screener
┌────────┬───────────┬────────────┬────────────┬───────────┬───────────┬──────────┬──────────────┬──────────────┬───────┬──────────────┬────────────┬───────┬────────┬──────────────┐
│ Ticker │ Perf Week │ Perf Month │ Perf Quart │ Perf Half │ Perf Year │ Perf YTD │ Volatility W │ Volatility M │ Recom │ Avg Volume   │ Rel Volume │ Price │ Change │ Volume       │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ YMAB   │ 0.07      │ -0.36      │ -0.62      │ -0.72     │ -0.83     │ -0.49    │ 0.17         │ 0.13         │ 1.90  │ 606550.00    │ 29.55      │ 8.25  │ 0.26   │ 12286763.00  │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ COE    │ 0.80      │ 0.45       │ -0.33      │ -0.36     │ -0.94     │ 0.31     │ 0.21         │ 0.14         │ 2.50  │ 287550.00    │ 8.88       │ 1.59  │ 0.23   │ 2292209.00   │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ KAVL   │ 1.09      │ 1.88       │ 0.22       │ -0.63     │ -0.93     │ 2.01     │ 0.41         │ 0.24         │       │ 5800000.00   │ 34.99      │ 2.24  │ 0.23   │ 131650688.00 │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ INCR   │ 0.30      │ 0.21       │ 0.04       │ 0.31      │ -0.12     │ 0.27     │ 0.10         │ 0.06         │       │ 93280.00     │ 19.04      │ 8.20  │ 0.22   │ 1396666.00   │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ RSVR   │ 0.14      │ -0.01      │ -0.26      │ -0.08     │ -0.35     │ -0.11    │ 0.12         │ 0.07         │ 2.00  │ 91770.00     │ 3.76       │ 7.02  │ 0.21   │ 332318.00    │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ COOP   │ 0.29      │ 0.14       │ 0.13       │ 0.28      │ 0.65      │ 0.18     │ 0.06         │ 0.04         │ 2.10  │ 872470.00    │ 5.13       │ 49.22 │ 0.19   │ 4171073.00   │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ AGFY   │ 0.26      │ -0.08      │ -0.57      │ -0.71     │ -0.55     │ -0.07    │ 0.14         │ 0.13         │ 2.00  │ 743420.00    │ 2.64       │ 8.51  │ 0.19   │ 1933556.00   │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ AZYO   │ 0.21      │ 0.02       │ 0.03       │ -0.24     │ -0.59     │ 0.02     │ 0.06         │ 0.10         │ 2.00  │ 15940.00     │ 1.02       │ 6.41  │ 0.19   │ 16694.00     │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ SNDL   │ 0.25      │ 0.14       │ -0.08      │ -0.12     │ -0.68     │ 0.15     │ 0.11         │ 0.09         │ 3.20  │ 107080000.00 │ 2.30       │ 0.66  │ 0.19   │ 246995920.00 │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ CRS    │ 0.34      │ 0.19       │ 0.16       │ 0.05      │ 0.08      │ 0.33     │ 0.09         │ 0.07         │ 2.50  │ 437500.00    │ 4.48       │ 38.73 │ 0.17   │ 1839490.00   │
└────────┴───────────┴────────────┴────────────┴───────────┴───────────┴──────────┴──────────────┴──────────────┴───────┴──────────────┴────────────┴───────┴────────┴──────────────┘

2022 Feb 14, 08:45 (✨) /stocks/scr/ $ performance -p head_shoulders_inverse
                                                                                   Finzin Screener
┌────────┬───────────┬────────────┬────────────┬───────────┬───────────┬──────────┬──────────────┬──────────────┬───────┬──────────────┬────────────┬───────┬────────┬──────────────┐
│ Ticker │ Perf Week │ Perf Month │ Perf Quart │ Perf Half │ Perf Year │ Perf YTD │ Volatility W │ Volatility M │ Recom │ Avg Volume   │ Rel Volume │ Price │ Change │ Volume       │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ YMAB   │ 0.07      │ -0.36      │ -0.62      │ -0.72     │ -0.83     │ -0.49    │ 0.17         │ 0.13         │ 1.90  │ 606550.00    │ 29.55      │ 8.25  │ 0.26   │ 12286763.00  │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ COE    │ 0.80      │ 0.45       │ -0.33      │ -0.36     │ -0.94     │ 0.31     │ 0.21         │ 0.14         │ 2.50  │ 287550.00    │ 8.88       │ 1.59  │ 0.23   │ 2292209.00   │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ KAVL   │ 1.09      │ 1.88       │ 0.22       │ -0.63     │ -0.93     │ 2.01     │ 0.41         │ 0.24         │       │ 5800000.00   │ 34.99      │ 2.24  │ 0.23   │ 131650688.00 │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ INCR   │ 0.30      │ 0.21       │ 0.04       │ 0.31      │ -0.12     │ 0.27     │ 0.10         │ 0.06         │       │ 93280.00     │ 19.04      │ 8.20  │ 0.22   │ 1396666.00   │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ RSVR   │ 0.14      │ -0.01      │ -0.26      │ -0.08     │ -0.35     │ -0.11    │ 0.12         │ 0.07         │ 2.00  │ 91770.00     │ 3.76       │ 7.02  │ 0.21   │ 332318.00    │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ COOP   │ 0.29      │ 0.14       │ 0.13       │ 0.28      │ 0.65      │ 0.18     │ 0.06         │ 0.04         │ 2.10  │ 872470.00    │ 5.13       │ 49.22 │ 0.19   │ 4171073.00   │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ AGFY   │ 0.26      │ -0.08      │ -0.57      │ -0.71     │ -0.55     │ -0.07    │ 0.14         │ 0.13         │ 2.00  │ 743420.00    │ 2.64       │ 8.51  │ 0.19   │ 1933556.00   │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ AZYO   │ 0.21      │ 0.02       │ 0.03       │ -0.24     │ -0.59     │ 0.02     │ 0.06         │ 0.10         │ 2.00  │ 15940.00     │ 1.02       │ 6.41  │ 0.19   │ 16694.00     │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ SNDL   │ 0.25      │ 0.14       │ -0.08      │ -0.12     │ -0.68     │ 0.15     │ 0.11         │ 0.09         │ 3.20  │ 107080000.00 │ 2.30       │ 0.66  │ 0.19   │ 246995920.00 │
├────────┼───────────┼────────────┼────────────┼───────────┼───────────┼──────────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼───────┼────────┼──────────────┤
│ CRS    │ 0.34      │ 0.19       │ 0.16       │ 0.05      │ 0.08      │ 0.33     │ 0.09         │ 0.07         │ 2.50  │ 437500.00    │ 4.48       │ 38.73 │ 0.17   │ 1839490.00   │
└────────┴───────────┴────────────┴────────────┴───────────┴───────────┴──────────┴──────────────┴──────────────┴───────┴──────────────┴────────────┴───────┴────────┴──────────────┘
```

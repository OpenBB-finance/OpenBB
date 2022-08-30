```
usage: ownership
                 [-p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}]
                 [-l LIMIT] [-a]
                 [-s {Ticker,Market Cap,Outstanding,Float,Insider Own,Insider Trans,Inst Own,Inst Trans,Float Short,Short Ratio,Avg Volume,Price,Change,Volume} [{Ticker,Market Cap,Outstanding,Float,Insider Own,Insider Trans,Inst Own,Inst Trans,Float Short,Short Ratio,Avg Volume,Price,Change,Volume} ...]]
                 [-h] [--export {csv,json,xlsx}]
```

Prints ownership data of the companies that meet the pre-set filtering. [Source: Finviz]

```
optional arguments:
  -p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}, --preset {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}
                        Filter presets
  -l LIMIT, --limit LIMIT
                        Limit of stocks to print
  -a, --ascend          Set order to Ascend, the default is Descend
  -s {Ticker,Market Cap,Outstanding,Float,Insider Own,Insider Trans,Inst Own,Inst Trans,Float Short,Short Ratio,Avg Volume,Price,Change,Volume} [{Ticker,Market Cap,Outstanding,Float,Insider Own,Insider Trans,Inst Own,Inst Trans,Float Short,Short Ratio,Avg Volume,Price,Change,Volume} ...], --sort {Ticker,Market Cap,Outstanding,Float,Insider Own,Insider Trans,Inst Own,Inst Trans,Float Short,Short Ratio,Avg Volume,Price,Change,Volume} [{Ticker,Market Cap,Outstanding,Float,Insider Own,Insider Trans,Inst Own,Inst Trans,Float Short,Short Ratio,Avg Volume,Price,Change,Volume} ...]
                        Sort elements of the table.
  -h, --help            show this help message
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx
```

```
2022 Feb 14, 08:43 (✨) /stocks/scr/ $ ownership -p top_performers_all
                                                                                      Finzin Screener
┌────────┬───────────────┬───────────────┬───────────────┬─────────────┬───────────────┬──────────┬────────────┬─────────────┬─────────────┬──────────────┬───────┬────────┬──────────────┐
│ Ticker │ Market Cap    │ Outstanding   │ Float         │ Insider Own │ Insider Trans │ Inst Own │ Inst Trans │ Float Short │ Short Ratio │ Avg Volume   │ Price │ Change │ Volume       │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ YMAB   │ 285860000.00  │ 43600000.00   │ 36580000.00   │ 0.01        │ -0.86         │ 0.68     │ -0.01      │ 0.05        │ 3.23        │ 606550.00    │ 8.25  │ 0.26   │ 12286763.00  │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ COE    │ 27700000.00   │ 21760000.00   │ 3690000.00    │ 0.02        │ 0.00          │ 0.82     │ 0.00       │ 0.05        │ 0.61        │ 287550.00    │ 1.59  │ 0.23   │ 2292209.00   │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ KAVL   │ 51610000.00   │ 28330000.00   │ 15950000.00   │ 0.60        │ 0.00          │ 0.02     │ 0.06       │ 0.03        │ 0.08        │ 5800000.00   │ 2.24  │ 0.23   │ 131650688.00 │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ INCR   │ 368950000.00  │ 44990000.00   │ 25770000.00   │ 0.40        │ 0.00          │ 0.12     │            │ 0.01        │ 1.45        │ 93280.00     │ 8.20  │ 0.22   │ 1396666.00   │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ RSVR   │ 371430000.00  │ 11060000.00   │               │ 0.02        │ 0.00          │ 0.42     │ 0.01       │             │ 11.42       │ 91770.00     │ 7.02  │ 0.21   │ 332318.00    │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ COOP   │ 3100000000.00 │ 78940000.00   │ 73640000.00   │ 0.02        │ -0.08         │ 0.89     │ 0.00       │ 0.03        │ 2.83        │ 872470.00    │ 49.22 │ 0.19   │ 4171073.00   │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ AGFY   │ 152330000.00  │ 20830000.00   │ 18820000.00   │ 0.00        │ -0.65         │ 0.32     │ 0.51       │ 0.11        │ 2.70        │ 743420.00    │ 8.51  │ 0.19   │ 1933556.00   │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ AZYO   │ 66790000.00   │ 10230000.00   │ 8560000.00    │ 0.00        │               │ 0.89     │ 0.23       │ 0.00        │ 0.06        │ 15940.00     │ 6.41  │ 0.19   │ 16694.00     │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ SNDL   │ 1150000000.00 │ 2050000000.00 │ 2040000000.00 │ 0.01        │ 0.00          │ 0.05     │ 0.21       │ 0.12        │ 2.31        │ 107080000.00 │ 0.66  │ 0.19   │ 246995920.00 │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ CRS    │ 1600000000.00 │ 48600000.00   │ 47320000.00   │ 0.01        │ 0.00          │ 0.92     │ -0.00      │ 0.03        │ 3.67        │ 437500.00    │ 38.73 │ 0.17   │ 1839490.00   │
└────────┴───────────────┴───────────────┴───────────────┴─────────────┴───────────────┴──────────┴────────────┴─────────────┴─────────────┴──────────────┴───────┴────────┴──────────────┘

2022 Feb 14, 08:43 (✨) /stocks/scr/ $ ownership -p double_bottom
                                                                                      Finzin Screener
┌────────┬───────────────┬───────────────┬───────────────┬─────────────┬───────────────┬──────────┬────────────┬─────────────┬─────────────┬──────────────┬───────┬────────┬──────────────┐
│ Ticker │ Market Cap    │ Outstanding   │ Float         │ Insider Own │ Insider Trans │ Inst Own │ Inst Trans │ Float Short │ Short Ratio │ Avg Volume   │ Price │ Change │ Volume       │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ YMAB   │ 285860000.00  │ 43600000.00   │ 36580000.00   │ 0.01        │ -0.86         │ 0.68     │ -0.01      │ 0.05        │ 3.23        │ 606550.00    │ 8.25  │ 0.26   │ 12286763.00  │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ COE    │ 27700000.00   │ 21760000.00   │ 3690000.00    │ 0.02        │ 0.00          │ 0.82     │ 0.00       │ 0.05        │ 0.61        │ 287550.00    │ 1.59  │ 0.23   │ 2292209.00   │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ KAVL   │ 51610000.00   │ 28330000.00   │ 15950000.00   │ 0.60        │ 0.00          │ 0.02     │ 0.06       │ 0.03        │ 0.08        │ 5800000.00   │ 2.24  │ 0.23   │ 131650688.00 │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ INCR   │ 368950000.00  │ 44990000.00   │ 25770000.00   │ 0.40        │ 0.00          │ 0.12     │            │ 0.01        │ 1.45        │ 93280.00     │ 8.20  │ 0.22   │ 1396666.00   │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ RSVR   │ 371430000.00  │ 11060000.00   │               │ 0.02        │ 0.00          │ 0.42     │ 0.01       │             │ 11.42       │ 91770.00     │ 7.02  │ 0.21   │ 332318.00    │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ COOP   │ 3100000000.00 │ 78940000.00   │ 73640000.00   │ 0.02        │ -0.08         │ 0.89     │ 0.00       │ 0.03        │ 2.83        │ 872470.00    │ 49.22 │ 0.19   │ 4171073.00   │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ AGFY   │ 152330000.00  │ 20830000.00   │ 18820000.00   │ 0.00        │ -0.65         │ 0.32     │ 0.51       │ 0.11        │ 2.70        │ 743420.00    │ 8.51  │ 0.19   │ 1933556.00   │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ AZYO   │ 66790000.00   │ 10230000.00   │ 8560000.00    │ 0.00        │               │ 0.89     │ 0.23       │ 0.00        │ 0.06        │ 15940.00     │ 6.41  │ 0.19   │ 16694.00     │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ SNDL   │ 1150000000.00 │ 2050000000.00 │ 2040000000.00 │ 0.01        │ 0.00          │ 0.05     │ 0.21       │ 0.12        │ 2.31        │ 107080000.00 │ 0.66  │ 0.19   │ 246995920.00 │
├────────┼───────────────┼───────────────┼───────────────┼─────────────┼───────────────┼──────────┼────────────┼─────────────┼─────────────┼──────────────┼───────┼────────┼──────────────┤
│ CRS    │ 1600000000.00 │ 48600000.00   │ 47320000.00   │ 0.01        │ 0.00          │ 0.92     │ -0.00      │ 0.03        │ 3.67        │ 437500.00    │ 38.73 │ 0.17   │ 1839490.00   │
└────────┴───────────────┴───────────────┴───────────────┴─────────────┴───────────────┴──────────┴────────────┴─────────────┴─────────────┴──────────────┴───────┴────────┴──────────────┘
```

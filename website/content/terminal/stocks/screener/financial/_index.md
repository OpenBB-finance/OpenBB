```
usage: financial
                 [-p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}]
                 [-l LIMIT] [-a]
                 [-s {Ticker,Market Cap,Dividend,ROA,ROE,ROI,Curr R,Quick R,LTDebt/Eq,Debt/Eq,Gross M,Oper M,Profit M,Earnings,Price,Change,Volume} [{Ticker,Market Cap,Dividend,ROA,ROE,ROI,Curr R,Quick R,LTDebt/Eq,Debt/Eq,Gross M,Oper M,Profit M,Earnings,Price,Change,Volume} ...]]
                 [-h] [--export {csv,json,xlsx}]
```

Prints financial data of the companies that meet the pre-set filtering. [Source: Finviz]

```
optional arguments:
  -p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}, --preset {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}
                        Filter presets
  -l LIMIT, --limit LIMIT
                        Limit of stocks to print
  -a, --ascend          Set order to Ascend, the default is Descend
  -s {Ticker,Market Cap,Dividend,ROA,ROE,ROI,Curr R,Quick R,LTDebt/Eq,Debt/Eq,Gross M,Oper M,Profit M,Earnings,Price,Change,Volume} [{Ticker,Market Cap,Dividend,ROA,ROE,ROI,Curr R,Quick R,LTDebt/Eq,Debt/Eq,Gross M,Oper M,Profit M,Earnings,Price,Change,Volume} ...], --sort {Ticker,Market Cap,Dividend,ROA,ROE,ROI,Curr R,Quick R,LTDebt/Eq,Debt/Eq,Gross M,Oper M,Profit M,Earnings,Price,Change,Volume} [{Ticker,Market Cap,Dividend,ROA,ROE,ROI,Curr R,Quick R,LTDebt/Eq,Debt/Eq,Gross M,Oper M,Profit M,Earnings,Price,Change,Volume} ...]
                        Sort elements of the table.
  -h, --help            show this help message
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx
```

```
                                                                                Finzin Screener
┌────────┬───────────────┬──────────┬───────┬───────┬───────┬────────┬─────────┬───────────┬─────────┬─────────┬────────┬──────────┬──────────┬───────┬────────┬──────────────┐
│ Ticker │ Market Cap    │ Dividend │ ROA   │ ROE   │ ROI   │ Curr R │ Quick R │ LTDebt/Eq │ Debt/Eq │ Gross M │ Oper M │ Profit M │ Earnings │ Price │ Change │ Volume       │
├────────┼───────────────┼──────────┼───────┼───────┼───────┼────────┼─────────┼───────────┼─────────┼─────────┼────────┼──────────┼──────────┼───────┼────────┼──────────────┤
│ YMAB   │ 285860000.00  │          │ -0.17 │ -0.19 │ -1.13 │ 9.10   │ 8.90    │ 0.00      │ 0.00    │ 0.98    │        │ -0.83    │ Nov 04/a │ 8.25  │ 0.26   │ 12286763.00  │
├────────┼───────────────┼──────────┼───────┼───────┼───────┼────────┼─────────┼───────────┼─────────┼─────────┼────────┼──────────┼──────────┼───────┼────────┼──────────────┤
│ COE    │ 27700000.00   │          │ 0.02  │ -0.05 │ -0.12 │ 0.50   │ 0.50    │           │         │ 0.73    │ 0.00   │ 0.02     │ -        │ 1.59  │ 0.23   │ 2292209.00   │
├────────┼───────────────┼──────────┼───────┼───────┼───────┼────────┼─────────┼───────────┼─────────┼─────────┼────────┼──────────┼──────────┼───────┼────────┼──────────────┤
│ KAVL   │ 51610000.00   │          │ -0.30 │ -1.12 │ 0.87  │ 1.40   │ 0.50    │ 0.00      │ 0.00    │ 0.21    │ -0.10  │ -0.11    │ -        │ 2.24  │ 0.23   │ 131650688.00 │
├────────┼───────────────┼──────────┼───────┼───────┼───────┼────────┼─────────┼───────────┼─────────┼─────────┼────────┼──────────┼──────────┼───────┼────────┼──────────────┤
│ INCR   │ 368950000.00  │          │       │       │       │        │         │           │         │         │        │          │ Nov 16/b │ 8.20  │ 0.22   │ 1396666.00   │
├────────┼───────────────┼──────────┼───────┼───────┼───────┼────────┼─────────┼───────────┼─────────┼─────────┼────────┼──────────┼──────────┼───────┼────────┼──────────────┤
│ RSVR   │ 371430000.00  │          │ -0.01 │ -0.01 │       │ 1.50   │ 1.50    │ 0.00      │ 0.00    │         │        │          │ Feb 08/b │ 7.02  │ 0.21   │ 332318.00    │
├────────┼───────────────┼──────────┼───────┼───────┼───────┼────────┼─────────┼───────────┼─────────┼─────────┼────────┼──────────┼──────────┼───────┼────────┼──────────────┤
│ COOP   │ 3100000000.00 │          │ 0.06  │ 0.48  │ 0.04  │        │         │ 3.15      │ 3.98    │         │ 0.48   │ 0.40     │ Feb 11/b │ 49.22 │ 0.19   │ 4171073.00   │
├────────┼───────────────┼──────────┼───────┼───────┼───────┼────────┼─────────┼───────────┼─────────┼─────────┼────────┼──────────┼──────────┼───────┼────────┼──────────────┤
│ AGFY   │ 152330000.00  │          │ -0.26 │ -0.31 │ -2.72 │ 5.80   │ 5.30    │ 0.01      │ 0.01    │ -0.02   │ -0.74  │ -0.83    │ Nov 10/b │ 8.51  │ 0.19   │ 1933556.00   │
├────────┼───────────────┼──────────┼───────┼───────┼───────┼────────┼─────────┼───────────┼─────────┼─────────┼────────┼──────────┼──────────┼───────┼────────┼──────────────┤
│ AZYO   │ 66790000.00   │          │ -0.29 │ -1.41 │ -0.31 │ 1.70   │ 1.30    │ 1.52      │ 2.78    │ 0.44    │ -0.33  │ -0.43    │ Nov 09/a │ 6.41  │ 0.19   │ 16694.00     │
├────────┼───────────────┼──────────┼───────┼───────┼───────┼────────┼─────────┼───────────┼─────────┼─────────┼────────┼──────────┼──────────┼───────┼────────┼──────────────┤
│ SNDL   │ 1150000000.00 │          │ -0.22 │ -0.24 │ -0.71 │ 13.40  │ 12.80   │ 0.02      │ 0.02    │ 0.08    │        │          │ Nov 11/a │ 0.66  │ 0.19   │ 246995920.00 │
├────────┼───────────────┼──────────┼───────┼───────┼───────┼────────┼─────────┼───────────┼─────────┼─────────┼────────┼──────────┼──────────┼───────┼────────┼──────────────┤
│ CRS    │ 1600000000.00 │ 0.02     │ -0.05 │ -0.10 │ -0.09 │ 3.50   │ 1.70    │ 0.52      │ 0.00    │ 0.02    │ -0.10  │ -0.09    │ Feb 02/b │ 38.73 │ 0.17   │ 1839490.00   │
└────────┴───────────────┴──────────┴───────┴───────┴───────┴────────┴─────────┴───────────┴─────────┴─────────┴────────┴──────────┴──────────┴───────┴────────┴──────────────┘
```

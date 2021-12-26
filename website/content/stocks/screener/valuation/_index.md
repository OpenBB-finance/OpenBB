```
usage: screener
                [-p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}]
                [-l LIMIT] [-a] [-s SORT [SORT ...]] [--export {csv,json,xlsx}] [-h]
```

Returns results from your chosen preset or signal focusing on valuation metrics. [Source: Finviz]

```
optional arguments:
  -p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}, --preset {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}
                        Filter presets
  -l LIMIT, --limit LIMIT
                        Limit of stocks to print
  -a, --ascend          Set order to Ascend, the default is Descend
  -s SORT [SORT ...], --sort SORT [SORT ...]
                        Sort elements of the table. Use Ticker, Market Cap, Dividend, ROA, ROE, ROI, Curr R, Quick R, LTDebt/Eq, Debt/Eq, Gross M, Oper M, Profit M, Earnings, Price, Change, Volume
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file
  -h, --help            show this help message
```

<img width="1400" alt="Feature Screenshot - screener-valuation" src="https://user-images.githubusercontent.com/85772166/144379581-7a6455bb-9228-4180-9929-1d7d50ed2533.png">


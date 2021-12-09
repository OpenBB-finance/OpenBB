```
usage: screener
                [-p {cheap_dividend,top_performers_all,top_performers_healthcare,potential_reversals,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,weak_support_and_top_performers,unusual_volume,bull_runs_over_10pct,modified_dreman,template,cheap_bottom_dividend,break_out_stocks,heavy_inst_ins,golden_cross,growth_stocks,value_stocks,sexy_year,5pct_above_low,buffett_like,death_cross,golden_cross_penny,oversold_under_3dol,short_squeeze_scan,cheap_oversold,continued_momentum_scan,top_performers_tech,analyst_strong_buy,oversold_under_5dol,modified_neff,oversold,rosenwald_gtfo,news_scanner,recent_growth_and_support,rosenwald,undervalue,high_vol_and_low_debt,under_15dol_stocks,channel_up_and_low_debt_and_sma_50and200}]
                [-s {top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}]
                [-l LIMIT] [-a] [-e] [-m] [-h]
```

Screen stocks based own share float and ownership data.

```
optional arguments:
  -p {cheap_dividend,top_performers_all,top_performers_healthcare,potential_reversals,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,weak_support_and_top_performers,unusual_volume,bull_runs_over_10pct,modified_dreman,template,cheap_bottom_dividend,break_out_stocks,heavy_inst_ins,golden_cross,growth_stocks,value_stocks,sexy_year,5pct_above_low,buffett_like,death_cross,golden_cross_penny,oversold_under_3dol,short_squeeze_scan,cheap_oversold,continued_momentum_scan,top_performers_tech,analyst_strong_buy,oversold_under_5dol,modified_neff,oversold,rosenwald_gtfo,news_scanner,recent_growth_and_support,rosenwald,undervalue,high_vol_and_low_debt,under_15dol_stocks,channel_up_and_low_debt_and_sma_50and200}, --preset {cheap_dividend,top_performers_all,top_performers_healthcare,potential_reversals,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,weak_support_and_top_performers,unusual_volume,bull_runs_over_10pct,modified_dreman,template,cheap_bottom_dividend,break_out_stocks,heavy_inst_ins,golden_cross,growth_stocks,value_stocks,sexy_year,5pct_above_low,buffett_like,death_cross,golden_cross_penny,oversold_under_3dol,short_squeeze_scan,cheap_oversold,continued_momentum_scan,top_performers_tech,analyst_strong_buy,oversold_under_5dol,modified_neff,oversold,rosenwald_gtfo,news_scanner,recent_growth_and_support,rosenwald,undervalue,high_vol_and_low_debt,under_15dol_stocks,channel_up_and_low_debt_and_sma_50and200}
                        Filter presets
  -s {top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}, --signal {top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}
                        Signal
  -l LIMIT, --limit LIMIT
                        Limit of stocks to print
  -a, --ascend          Set order to Ascend, the default is Descend
  -e, --export          Save list as a text file
  -m, --mill            Run papermill on list
  -h, --help            show this help message
```

<img width="1400" alt="ownership" src="https://user-images.githubusercontent.com/85772166/144373196-8188b796-6a14-4322-b263-61d743c5e25e.png">

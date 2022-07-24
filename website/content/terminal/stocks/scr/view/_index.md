```
usage: view
            [-p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers}]
            [-h]
```

View available presets.

```
optional arguments:
  -p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers}, --preset {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers}
                        View specific custom preset
  -h, --help            show this help message
```

```
Custom Presets:
   5pct_above_low                                    5% Above Low
   analyst_strong_buy                                Analyst Strong Buy
   break_out_stocks                                  Break out Stocks
   buffett_like                                      Buffet like value screener (Value invsting for long term growth)
   bull_runs_over_10pct                              Bull runs over 10%
   channel_up_and_low_debt_and_sma_50and200          (Channel Up, Low Debt, Above 50 & 200 SMA)
   cheap_bottom_dividend                             High Yield Dividend stonks that are at-or-near their lowest price. Inverse Head and shoulders pattern recognized.
   cheap_dividend                                    Cheap dividend stocks
   cheap_oversold                                    Cheap stonks that are oversold: under 10% above the low, and oversold on the RSI.
   continued_momentum_scan                           Continued Momentum Scan
   death_cross                                       When the 50 sma crosses below the 200 sma. More information can be found in https://www.investopedia.com/terms/d/deathcross.asp
   golden_cross                                      Golden Cross when the 50 day moves above the200 day from below.
   golden_cross_penny                                Golden Cross
   growth_stocks                                     Growth Stocks
   heavy_inst_ins                                    Heavily owned by institutions and insiders (>30% each)
   high_vol_and_low_debt                             High Volume, NEW Volume, Low Debt
   modified_dreman                                   Modified Version of the Dreman Screener.
   modified_neff                                     Neff Screener with modifications // operational margin <50%. More information can be found in https://marketxls.com/template/neff-screen/
   news_scanner                                      News Scanner
   oversold                                          Oversold
   oversold_under_3dol                               Oversold Under $3
   oversold_under_5dol                               Oversold Under $5
   potential_reversals                               Potential Reversals
   recent_growth_and_support                         Recent Growth, Support
   rosenwald                                         The "classic rosenwald" screen based on some dude i work with best guess.
   rosenwald_gtfo                                    Too many indicators indicating an impending crash.
   sexy_year                                         This is just a sample. The user that adds the preset can add a description for what type of stocks these filters are aimed for
   short_squeeze_scan                                Short Squeeze Scan
   simplistic_momentum_scanner_under_7dol            Simplistic Momentum Scanner Under $7
   stocks_strong_support_levels                      Stocks Strong Support Levels
   template                                          Template with all available filters and their options menu. More information can be found in https://finviz.com/help/screener.ashx and https://finviz.com/help/technical-analysis/charts-patterns.ashx
   top_performers_all                                Top performers (ALL)
   top_performers_healthcare                         Top performers (Healthcare)
   top_performers_tech                               Top performers (tech)
   undervalue                                        Potential Undervalued stocks
   under_15dol_stocks                                Under $15 Stocks
   unusual_volume                                    Unusual Volume
   value_stocks                                      Value Stocks
   weak_support_and_top_performers                   (Weak Support Trendlines, Top Performers)

Default Presets:
   top_gainers                                       stocks with the highest %% price gain today
   top_losers                                        stocks with the highest %% price loss today
   new_high                                          stocks making 52-week high today
   new_low                                           stocks making 52-week low today
   most_volatile                                     stocks with the highest widest high/low trading range today
   most_active                                       stocks with the highest trading volume today
   unusual_volume                                    stocks with unusually high volume today - the highest relative volume ratio
   overbought                                        stock is becoming overvalued and may experience a pullback.
   oversold                                          oversold stocks may represent a buying opportunity for investors
   downgrades                                        stocks downgraded by analysts today
   upgrades                                          stocks upgraded by analysts today
   earnings_before                                   companies reporting earnings today, before market open
   earnings_after                                    companies reporting earnings today, after market close
   recent_insider_buying                             stocks with recent insider buying activity
   recent_insider_selling                            stocks with recent insider selling activity
   major_news                                        stocks with the highest news coverage today
   horizontal_sr                                     horizontal channel of price range between support and resistance trendlines
   tl_resistance                                     once a rising trendline is broken
   tl_support                                        once a falling trendline is broken
   wedge_up                                          upward trendline support and upward trendline resistance (reversal)
   wedge_down                                        downward trendline support and downward trendline resistance (reversal)
   wedge                                             upward trendline support, downward trendline resistance (contiunation)
   triangle_ascending                                upward trendline support and horizontal trendline resistance
   triangle_descending                               horizontal trendline support and downward trendline resistance
   channel_up                                        both support and resistance trendlines slope upward
   channel_down                                      both support and resistance trendlines slope downward
   channel                                           both support and resistance trendlines are horizontal
   double_top                                        stock with 'M' shape that indicates a bearish reversal in trend
   double_bottom                                     stock with 'W' shape that indicates a bullish reversal in trend
   multiple_top                                      same as double_top hitting more highs
   multiple_bottom                                   same as double_bottom hitting more lows
   head_shoulders                                    chart formation that predicts a bullish-to-bearish trend reversal
   head_shoulders_inverse                            chart formation that predicts a bearish-to-bullish trend reversal
```

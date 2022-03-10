```
usage: overview
                [-p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}]
                [-l LIMIT] [-a] [-s {Ticker,Company,Sector,Industry,Country,Market Cap,P/E,Price,Change,Volume} [{Ticker,Company,Sector,Industry,Country,Market Cap,P/E,Price,Change,Volume} ...]] [-h] [--export {csv,json,xlsx}]
```

Prints overview data of the companies that meet the pre-set filtering. [Source: Finviz]

```
optional arguments:
  -p {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}, --preset {5pct_above_low,analyst_strong_buy,break_out_stocks,buffett_like,bull_runs_over_10pct,channel_up_and_low_debt_and_sma_50and200,cheap_bottom_dividend,cheap_dividend,cheap_oversold,continued_momentum_scan,death_cross,golden_cross,golden_cross_penny,growth_stocks,heavy_inst_ins,high_vol_and_low_debt,modified_dreman,modified_neff,news_scanner,oversold,oversold_under_3dol,oversold_under_5dol,potential_reversals,recent_growth_and_support,rosenwald,rosenwald_gtfo,sexy_year,short_squeeze_scan,simplistic_momentum_scanner_under_7dol,stocks_strong_support_levels,template,top_performers_all,top_performers_healthcare,top_performers_tech,undervalue,under_15dol_stocks,unusual_volume,value_stocks,weak_support_and_top_performers,top_gainers,top_losers,new_high,new_low,most_volatile,most_active,unusual_volume,overbought,oversold,downgrades,upgrades,earnings_before,earnings_after,recent_insider_buying,recent_insider_selling,major_news,horizontal_sr,tl_resistance,tl_support,wedge_up,wedge_down,wedge,triangle_ascending,triangle_descending,channel_up,channel_down,channel,double_top,double_bottom,multiple_top,multiple_bottom,head_shoulders,head_shoulders_inverse}
                        Filter presets
  -l LIMIT, --limit LIMIT
                        Limit of stocks to print
  -a, --ascend          Set order to Ascend, the default is Descend
  -s {Ticker,Company,Sector,Industry,Country,Market Cap,P/E,Price,Change,Volume} [{Ticker,Company,Sector,Industry,Country,Market Cap,P/E,Price,Change,Volume} ...], --sort {Ticker,Company,Sector,Industry,Country,Market Cap,P/E,Price,Change,Volume} [{Ticker,Company,Sector,Industry,Country,Market Cap,P/E,Price,Change,Volume} ...]
                        Sort elements of the table.
  -h, --help            show this help message
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx
```

```
2022 Feb 14, 08:40 (✨) /stocks/scr/ $ overview -p buffett_like
                                                                                    Finzin Screener
┌────────┬───────────────────────────────────────┬────────────────────────┬──────────────────────────────────────────┬─────────┬───────────────┬──────┬───────┬────────┬──────────────┐
│ Ticker │ Company                               │ Sector                 │ Industry                                 │ Country │ Market Cap    │ P/E  │ Price │ Change │ Volume       │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ YMAB   │ Y-mAbs Therapeutics, Inc.             │ Healthcare             │ Biotechnology                            │ USA     │ 285860000.00  │      │ 8.25  │ 0.26   │ 12286763.00  │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ COE    │ China Online Education Group          │ Consumer Defensive     │ Education & Training Services            │ China   │ 27700000.00   │ 5.39 │ 1.59  │ 0.23   │ 2292209.00   │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ KAVL   │ Kaival Brands Innovations Group, Inc. │ Consumer Defensive     │ Tobacco                                  │ USA     │ 51610000.00   │      │ 2.24  │ 0.23   │ 131650688.00 │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ INCR   │ InterCure Ltd.                        │ Healthcare             │ Drug Manufacturers - Specialty & Generic │ Israel  │ 368950000.00  │      │ 8.20  │ 0.22   │ 1396666.00   │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ RSVR   │ Reservoir Media, Inc.                 │ Communication Services │ Entertainment                            │ USA     │ 371430000.00  │      │ 7.02  │ 0.21   │ 332318.00    │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ COOP   │ Mr. Cooper Group Inc.                 │ Financial              │ Mortgage Finance                         │ USA     │ 3100000000.00 │ 3.03 │ 49.22 │ 0.19   │ 4171073.00   │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ AGFY   │ Agrify Corporation                    │ Industrials            │ Engineering & Construction               │ USA     │ 152330000.00  │      │ 8.51  │ 0.19   │ 1933556.00   │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ AZYO   │ Aziyo Biologics, Inc.                 │ Healthcare             │ Medical Devices                          │ USA     │ 66790000.00   │      │ 6.41  │ 0.19   │ 16694.00     │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ SNDL   │ Sundial Growers Inc.                  │ Healthcare             │ Drug Manufacturers - Specialty & Generic │ Canada  │ 1150000000.00 │      │ 0.66  │ 0.19   │ 246995920.00 │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ CRS    │ Carpenter Technology Corporation      │ Industrials            │ Metal Fabrication                        │ USA     │ 1600000000.00 │      │ 38.73 │ 0.17   │ 1839490.00   │
└────────┴───────────────────────────────────────┴────────────────────────┴──────────────────────────────────────────┴─────────┴───────────────┴──────┴───────┴────────┴──────────────┘

2022 Feb 14, 08:40 (✨) /stocks/scr/ $ overview -p channel_up
                                                                                    Finzin Screener
┌────────┬───────────────────────────────────────┬────────────────────────┬──────────────────────────────────────────┬─────────┬───────────────┬──────┬───────┬────────┬──────────────┐
│ Ticker │ Company                               │ Sector                 │ Industry                                 │ Country │ Market Cap    │ P/E  │ Price │ Change │ Volume       │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ YMAB   │ Y-mAbs Therapeutics, Inc.             │ Healthcare             │ Biotechnology                            │ USA     │ 285860000.00  │      │ 8.25  │ 0.26   │ 12286763.00  │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ COE    │ China Online Education Group          │ Consumer Defensive     │ Education & Training Services            │ China   │ 27700000.00   │ 5.39 │ 1.59  │ 0.23   │ 2292209.00   │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ KAVL   │ Kaival Brands Innovations Group, Inc. │ Consumer Defensive     │ Tobacco                                  │ USA     │ 51610000.00   │      │ 2.24  │ 0.23   │ 131650688.00 │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ INCR   │ InterCure Ltd.                        │ Healthcare             │ Drug Manufacturers - Specialty & Generic │ Israel  │ 368950000.00  │      │ 8.20  │ 0.22   │ 1396666.00   │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ RSVR   │ Reservoir Media, Inc.                 │ Communication Services │ Entertainment                            │ USA     │ 371430000.00  │      │ 7.02  │ 0.21   │ 332318.00    │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ COOP   │ Mr. Cooper Group Inc.                 │ Financial              │ Mortgage Finance                         │ USA     │ 3100000000.00 │ 3.03 │ 49.22 │ 0.19   │ 4171073.00   │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ AGFY   │ Agrify Corporation                    │ Industrials            │ Engineering & Construction               │ USA     │ 152330000.00  │      │ 8.51  │ 0.19   │ 1933556.00   │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ AZYO   │ Aziyo Biologics, Inc.                 │ Healthcare             │ Medical Devices                          │ USA     │ 66790000.00   │      │ 6.41  │ 0.19   │ 16694.00     │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ SNDL   │ Sundial Growers Inc.                  │ Healthcare             │ Drug Manufacturers - Specialty & Generic │ Canada  │ 1150000000.00 │      │ 0.66  │ 0.19   │ 246995920.00 │
├────────┼───────────────────────────────────────┼────────────────────────┼──────────────────────────────────────────┼─────────┼───────────────┼──────┼───────┼────────┼──────────────┤
│ CRS    │ Carpenter Technology Corporation      │ Industrials            │ Metal Fabrication                        │ USA     │ 1600000000.00 │      │ 38.73 │ 0.17   │ 1839490.00   │
└────────┴───────────────────────────────────────┴────────────────────────┴──────────────────────────────────────────┴─────────┴───────────────┴──────┴───────┴────────┴──────────────┘
```

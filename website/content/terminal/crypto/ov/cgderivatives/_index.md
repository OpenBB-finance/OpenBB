```
usage: cgderivatives [-l N] [-s {Rank,Market,Symbol,Price,Pct_Change_24h,Contract_Type,Basis,Spread,Funding_Rate,Volume_24h}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Shows list of crypto derivatives from CoinGecko Crypto derivatives are secondary contracts or financial tools that derive their value from a primary
underlying asset. In this case, the primary asset would be a cryptocurrency such as Bitcoin. The most popular crypto derivatives are crypto futures,
crypto options, and perpetual contracts. You can look on only display N number records with --limit, You can sort by Rank, Market, Symbol, Price,
Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate, Volume_24h with --sort and also with --descend flag to set it to sort descending.
Displays: Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate, Volume_24h

```
optional arguments:
  -l N, --limit N     display N number records (default: 15)
  -s {Rank,Market,Symbol,Price,Pct_Change_24h,Contract_Type,Basis,Spread,Funding_Rate,Volume_24h}, --sort {Rank,Market,Symbol,Price,Pct_Change_24h,Contract_Type,Basis,Spread,Funding_Rate,Volume_24h}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:11 (✨) /crypto/ov/ $ cgderivatives
                                                                 Crypto Derivatives
┌──────┬───────────────────────────────┬───────────────┬──────────┬────────────────┬───────────────┬───────┬────────┬──────────────┬────────────────┐
│ Rank │ Market                        │ Symbol        │ Price    │ Pct_Change_24h │ Contract_Type │ Basis │ Spread │ Funding_Rate │ Volume_24h     │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 1    │ Binance (Futures)             │ BTCUSDT       │ 44268.84 │ 4.20           │ perpetual     │ 0.02  │ 0.01   │ -0.01        │ 14058514627.71 │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 2    │ FTX (Derivatives)             │ BTC-PERP      │ 44320.00 │ 4.26           │ perpetual     │ -0.07 │ 0.01   │ 0.05         │ 3855173273.68  │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 3    │ MEXC Global (Futures)         │ ETH_USDT      │ 3113.88  │ 6.05           │ perpetual     │ 0.06  │ 0.01   │ -0.02        │ 742832083.24   │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 4    │ Gate.io (Futures)             │ BTC_USDT      │ 44255.93 │ 4.07           │ perpetual     │ 0.07  │ 0.01   │ -0.01        │ 1323562150.90  │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 5    │ Binance (Futures)             │ ETHUSDT       │ 3116.95  │ 6.44           │ perpetual     │ 0.04  │ 0.01   │ -0.02        │ 6311502301.53  │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 6    │ Prime XBT                     │ BTC/USD       │ 44250.70 │ 4.25           │ perpetual     │ 0.00  │ 0.02   │ 0.00         │ 237445592.24   │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 7    │ Bitget Futures                │ BTCUSDT_UMCBL │ 44240.81 │ 3.93           │ perpetual     │ -0.01 │ 0.01   │ -0.01        │ 4770121162.81  │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 8    │ FTX (Derivatives)             │ ETH-PERP      │ 3115.00  │ 6.25           │ perpetual     │ 0.03  │ 0.01   │ 0.00         │ 2193700085.40  │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 9    │ Bitfinex (Futures)            │ ETHF0:USTF0   │ 3116.90  │ 6.59           │ perpetual     │ 0.05  │ 0.01   │ 0.00         │ 35390334.64    │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 10   │ Bybit                         │ BTCUSDT       │ 44213.89 │ 3.90           │ perpetual     │ 0.06  │ 0.01   │ -0.01        │ 2873696641.99  │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 11   │ C-Trade                       │ BTCUSD        │ 44172.50 │ 3.65           │ perpetual     │ 0.16  │ 0.01   │ 0.01         │ 25634007.98    │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 12   │ Crypto.com Exchange (Futures) │ BTCUSD-PERP   │ 44295.00 │ 4.21           │ perpetual     │ -0.00 │ 0.02   │ 0.00         │ 882778425.04   │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 13   │ Binance (Futures)             │ BTCUSD_PERP   │ 44273.80 │ 4.16           │ perpetual     │ 0.05  │ 0.01   │ -0.01        │ 5207414861.13  │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 14   │ Bybit                         │ BTCUSD        │ 44200.50 │ 3.89           │ perpetual     │ 0.10  │ 0.01   │ -0.01        │ 1365988606.18  │
├──────┼───────────────────────────────┼───────────────┼──────────┼────────────────┼───────────────┼───────┼────────┼──────────────┼────────────────┤
│ 15   │ BTSE (Futures)                │ BTCPFC        │ 44220.00 │ 4.10           │ perpetual     │ 0.03  │ 0.01   │ 0.00         │ 1022965434.27  │
└──────┴───────────────────────────────┴───────────────┴──────────┴────────────────┴───────────────┴───────┴────────┴──────────────┴────────────────┘
```

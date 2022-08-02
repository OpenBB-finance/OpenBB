```
usage: cgindexes [-l N] [-s {Rank,Name,Id,Market,Last,MultiAsset}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Shows list of crypto indexes from CoinGecko. Each crypto index is made up of a selection of cryptocurrencies, grouped together and weighted by market
cap. You can display only N number of indexes with --limit parameter. You can sort data by Rank, Name, Id, Market, Last, MultiAsset with --sort and
also with --descend flag to sort descending. Displays: Rank, Name, Id, Market, Last, MultiAsset

```
optional arguments:
  -l N, --limit N     display N number records (default: 15)
  -s {Rank,Name,Id,Market,Last,MultiAsset}, --sort {Rank,Name,Id,Market,Last,MultiAsset}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:13 (✨) /crypto/ov/ $ cgindexes
                                       Crypto Indexes
┌──────┬─────────────────────────────┬────────┬───────────────────────┬───────┬────────────┐
│ Rank │ Name                        │ Id     │ Market                │ Last  │ MultiAsset │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 1    │ CoinFLEX (Futures) DFN      │ DFN    │ CoinFLEX (Futures)    │ nan   │ None       │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 2    │ Perpetual Protocol ZIL      │ ZIL    │ Perpetual Protocol    │ 0.11  │ None       │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 3    │ Bibox (Futures) LINK        │ LINK   │ Bibox (Futures)       │ 0.11  │ None       │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 4    │ CME Bitcoin Futures BTC     │ BTC    │ CME Group             │ 0.11  │ False      │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 5    │ Bibox (Futures) XRP         │ XRP    │ Bibox (Futures)       │ 0.11  │ None       │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 6    │ Bibox (Futures) AXS         │ AXS    │ Bibox (Futures)       │ 0.11  │ None       │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 7    │ ZBG Futures BSV             │ BSV    │ ZBG Futures           │ 0.11  │ None       │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 8    │ MEXC Global (Futures) ATLAS │ ATLAS  │ MEXC Global (Futures) │ 4.54  │ None       │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 9    │ CoinFLEX (Futures) BCHABC   │ BCHABC │ CoinFLEX (Futures)    │ 0.00  │ None       │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 10   │ Prime XBT USDC              │ USDC   │ Prime XBT             │ 0.00  │ None       │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 11   │ Poloniex Futures AXS        │ AXS    │ Poloniex Futures      │ 60.56 │ None       │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 12   │ Bibox (Futures) ETC         │ ETC    │ Bibox (Futures)       │ 60.56 │ None       │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 13   │ MyCoinStory SUN             │ SUN    │ MCS                   │ 13.41 │ None       │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 14   │ dYdX                        │ DYDX   │ FTX (Derivatives)     │ 7.57  │ None       │
├──────┼─────────────────────────────┼────────┼───────────────────────┼───────┼────────────┤
│ 15   │ Ronin                       │ RON    │ FTX (Derivatives)     │ 2.83  │ False      │
└──────┴─────────────────────────────┴────────┴───────────────────────┴───────┴────────────┘
```

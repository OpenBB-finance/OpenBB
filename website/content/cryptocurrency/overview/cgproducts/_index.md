```
usage: cgproducts [-l N] [-s {Rank,Platform,Identifier,Supply_Rate,Borrow_Rate}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Shows Top Crypto Financial Products with which you can earn yield, borrow or lend your crypto. You can display only N number of platforms with
--limit parameter. You can sort data by Rank, Platform, Identifier, Supply_Rate, Borrow_Rate with --sort and also with --descend flag to sort
descending. Displays: Rank, Platform, Identifier, Supply_Rate, Borrow_Rate

```
optional arguments:
  -l N, --limit N     display N number records (default: 15)
  -s {Rank,Platform,Identifier,Supply_Rate,Borrow_Rate}, --sort {Rank,Platform,Identifier,Supply_Rate,Borrow_Rate}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:15 (✨) /crypto/ov/ $ cgproducts
                        Financial Products
┌──────┬─────────────────┬────────────┬─────────────┬─────────────┐
│ Rank │ Platform        │ Identifier │ Supply_Rate │ Borrow_Rate │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 1    │ Crypto.com      │ DAI        │ 6.0         │ None        │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 2    │ Inlock          │ USDC       │ 10.2        │ None        │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 3    │ Staked US       │ Keep       │ 3.4         │ None        │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 4    │ Binance Savings │ XTZ001     │ 1.956035    │ None        │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 5    │ Staked US       │ V-Systems  │ 17.8        │ None        │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 6    │ Binance Savings │ ZEC001     │ 0.182865    │ None        │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 7    │ Binance Savings │ UNI001     │ 1.0001      │ None        │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 8    │ Binance Savings │ WAVES001   │ 5.000135    │ None        │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 9    │ Nexo            │ PAXG       │ 8.0         │ 0.001       │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 10   │ Crypto.com      │ BNB        │ 2.0         │ None        │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 11   │ Staked US       │ Dai        │ 4.212       │ None        │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 12   │ Celsius Network │ SOL        │ 5.36        │ None        │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 13   │ Celsius Network │ SGB        │ 0.0         │ None        │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 14   │ Nexo            │ GBP        │ 12.0        │ None        │
├──────┼─────────────────┼────────────┼─────────────┼─────────────┤
│ 15   │ Binance Savings │ BAL001     │ 4.20991     │ None        │
└──────┴─────────────────┴────────────┴─────────────┴─────────────┘
```

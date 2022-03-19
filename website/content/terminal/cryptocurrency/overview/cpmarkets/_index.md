```
usage: cpmarkets
                 [--vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}]
                 [-l N] [-s {rank,name,symbol,price,volume_24h,mcap_change_24h,pct_change_1h,pct_change_24h,ath_price,pct_from_ath}] [--descend]
                 [--export {csv,json,xlsx}] [-h]
```

Show market related (price, supply, volume) coin information for all coins on CoinPaprika. You can display only N number of coins with --limit
parameter. You can sort data by rank, name, symbol, price, volume_24h, mcap_change_24h, pct_change_1h, pct_change_24h, ath_price, pct_from_ath,
--sort parameter and also with --descend flag to sort descending. Displays: rank, name, symbol, price, volume_24h, mcap_change_24h, pct_change_1h,
pct_change_24h, ath_price, pct_from_ath,

```
optional arguments:
  --vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}
                        Quoted currency. Default USD (default: USD)
  -l N, --limit N     Limit of records (default: 15)
  -s {rank,name,symbol,price,volume_24h,mcap_change_24h,pct_change_1h,pct_change_24h,ath_price,pct_from_ath}, --sort {rank,name,symbol,price,volume_24h,mcap_change_24h,pct_change_1h,pct_change_24h,ath_price,pct_from_ath}
                        Sort by given column. Default: rank (default: rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:19 (✨) /crypto/ov/ $ cpmarkets

Displaying data vs USD
                                                          Basic Market Information
┌──────┬───────────────────┬────────────┬────────┬────────────┬─────────────────┬───────────────┬────────────────┬───────────┬──────────────┐
│ rank │ name              │ symbol     │ price  │ volume_24h │ mcap_change_24h │ pct_change_1h │ pct_change_24h │ ath_price │ pct_from_ath │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ ZcCoin            │ ZCC        │ 0.004  │ 1.249 K    │ 0               │ -0.230        │ -1.290         │ 0.014     │ -72.510      │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ Icolcoin          │ ICOL       │ 0.011  │ 0.000      │ 0               │ -0.040        │ 3.100          │ 1.099     │ -98.990      │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ Poodle Dog Coin   │ POODLE DOG │ 0.000  │ 635.137    │ 0               │ 0             │ 0              │ nan       │ nan          │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ REDANCOIN         │ REDAN      │ 0.006  │ 396.232    │ 0               │ -0.040        │ 4.110          │ 0.017     │ -66.030      │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ Fado Go           │ FADO       │ 0.010  │ 10.257 M   │ 0               │ 1.250         │ -25.140        │ 0.021     │ -49.900      │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ OK Fly            │ OKFLY      │ 0.000  │ 178.900    │ 0               │ -0.340        │ 0.540          │ 0.000     │ -6.600       │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ Leonardo SPA      │ LDO        │ 7.623  │ 53.360     │ 0               │ -0.260        │ -0.180         │ 8.860     │ -13.930      │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ HappyDoge         │ HAPPYDOGE  │ 0.000  │ 56.544     │ 0               │ -0.210        │ -5             │ 0.000     │ -23.840      │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ Hyper DAO         │ HDAO       │ 0.030  │ 4.797      │ 0               │ -0.230        │ -0.130         │ 0.031     │ -2.500       │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ SweetGirl         │ SWTG       │ 0.001  │ 16.067     │ 0               │ -0.210        │ 6.340          │ 0.001     │ -1           │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ Gaj Finance       │ GAJ        │ 0.047  │ 598.888    │ 5.090           │ 0.280         │ 5.090          │ 0.568     │ -91.780      │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ Noachis Terra     │ NTT        │ 0.000  │ 1.263      │ 0               │ -0.210        │ 6.250          │ 0.000     │ -85.260      │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ Connect Coin      │ XCON       │ 0.000  │ 25.370     │ -2.620          │ -0.040        │ -2.620         │ 0.696     │ -99.960      │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ ECOSCU            │ ECU        │ 0.003  │ 21.205     │ 0               │ -0.210        │ 1.680          │ 0.004     │ -23.090      │
├──────┼───────────────────┼────────────┼────────┼────────────┼─────────────────┼───────────────┼────────────────┼───────────┼──────────────┤
│ 0    │ Under Armour Cl A │ UAA        │ 17.190 │ 429.750    │ 0               │ 0             │ -1.770         │ 27.140    │ -36.660      │
└──────┴───────────────────┴────────────┴────────┴────────────┴─────────────────┴───────────────┴────────────────┴───────────┴──────────────┘
```

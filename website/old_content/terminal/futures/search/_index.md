```
usage: search [-e {NYB,CMX,CME,CBT,NYM}] [-c {metals,agriculture,index,hydrocarbon,bonds,currency}] [-d DESCRIPTION [DESCRIPTION ...]] [-h] [--export EXPORT]
```

Search futures. [Source: YahooFinance]

```
optional arguments:
  -e {NYB,CMX,CME,CBT,NYM}, --exchange {NYB,CMX,CME,CBT,NYM}
                        Select the exchange where the future exists (default: )
  -c {metals,agriculture,index,hydrocarbon,bonds,currency}, --category {metals,agriculture,index,hydrocarbon,bonds,currency}
                        Select the category where the future exists (default: )
  -d DESCRIPTION [DESCRIPTION ...], --description DESCRIPTION [DESCRIPTION ...]
                        Select the description future you are interested in (default: )
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
```

```
2022 Oct 18, 19:08 (🦋) /futures/ $ search -d silver

┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┓
┃ Ticker ┃ Description                  ┃ Exchange ┃ Category ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━┩
│ YI     │ 1,000 oz Mini Silver Futures │ NYB      │ metals   │
├────────┼──────────────────────────────┼──────────┼──────────┤
│ QI     │ E-mini Silver Futures        │ CMX      │ metals   │
├────────┼──────────────────────────────┼──────────┼──────────┤
│ SIL    │ E-mini Micro Silver Futures  │ CMX      │ metals   │
├────────┼──────────────────────────────┼──────────┼──────────┤
│ SIT    │ Silver TAS Futures           │ CMX      │ metals   │
└────────┴──────────────────────────────┴──────────┴──────────┘


2022 Oct 18, 19:10 (🦋) /futures/ $ search -c metals --exchange NYB

┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┓
┃ Ticker ┃ Description                  ┃ Exchange ┃ Category ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━┩
│ YI     │ 1,000 oz Mini Silver Futures │ NYB      │ metals   │
├────────┼──────────────────────────────┼──────────┼──────────┤
│ YG     │ E-mini Gold Futures          │ NYB      │ metals   │
└────────┴──────────────────────────────┴──────────┴──────────┘
```
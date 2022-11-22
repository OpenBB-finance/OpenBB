`usage: il [-pcA PRICECHANGEA] [-pcB PRICECHANGEB] [-p PROPORTION] [-v VALUE] [-n] [-h] [--export EXPORT`

Tool to calculate Impermanent Loss in a custom liquidity pool. Users can provide percentages increases for two tokens (and their weight in
the liquidity pool) and verify the impermanent loss that can occur.

```
optional arguments:
  -pcA PRICECHANGEA, --priceChangeA PRICECHANGEA
                        Token A price change in percentage (default: 0)
  -pcB PRICECHANGEB, --priceChangeB PRICECHANGEB
                        Token B price change in percentage (default: 100)
  -p PROPORTION, --proportion PROPORTION
                        Pool proportion. E.g., 50 means that pool contains 50% of token A and 50% of token B, 30 means that pool contains
                        30% of token A and 70% of token B (default: 50)
  -v VALUE, --value VALUE
                        Initial amount of dollars that user provides to liquidity pool (default: 1000)
  -n, --narrative       Flag to show narrative instead of dataframe (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
```

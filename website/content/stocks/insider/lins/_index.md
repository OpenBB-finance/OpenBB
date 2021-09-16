```
usage: lins [-n N_NUM] [--export {csv,json,xlsx}] [-h]
```

Prints information about inside traders. The following fields are expected: Date, Relationship, Transaction, #Shares, Cost, Value ($), #Shares Total, Insider Trading, SEC Form 4. [Source: Finviz]

```
optional arguments:
  -n N_NUM, --num N_NUM
                        number of latest inside traders.
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file
  -h, --help            show this help message
```

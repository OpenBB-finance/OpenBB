```
usage: arkord [-n N_NUM] [-s {date,volume,open,high,close,low,total,weight,shares} [{date,volume,open,high,close,low,total,weight,shares} ...]] [-a]
              [-b] [-c] [-f {ARKK,ARKF,ARKW,ARKQ,ARKG,ARKX,}] [--export {csv,json,xlsx}] [-h]
```

Track the orders by ARK Investment Management LLC with an exportable table - https://cathiesark.com/ark-funds-combined/complete-holdings

```
optional arguments:
  -n N_NUM, --num N_NUM
                        Last N ARK orders. (default: 10)
  -s {date,volume,open,high,close,low,total,weight,shares} [{date,volume,open,high,close,low,total,weight,shares} ...], --sortby {date,volume,open,high,close,low,total,weight,shares} [{date,volume,open,high,close,low,total,weight,shares} ...]
                        Colume to sort by (default: )
  -a, -ascend           Flag to sort in ascending order (default: False)
  -b, --buy_only        Flag to look at buys only (default: False)
  -c, --sell_only       Flag to look at sells only (default: False)
  -f {ARKK,ARKF,ARKW,ARKQ,ARKG,ARKX,}, --fund {ARKK,ARKF,ARKW,ARKQ,ARKG,ARKX,}
                        Filter by fund (default: )
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
<img width="1398" alt="Feature Screenshot - Arkord" src="https://user-images.githubusercontent.com/85772166/140194017-83b5ee53-66e3-4fe4-92e2-b6e46184e7a3.png">

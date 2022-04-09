```
usage: book [-l {5,10,20,50,100,500,1000,5000}] [--vs {USDT,TUSD,USDC,BUSD,NGN,RUB,TRY,EUR,IDRT,GBP,UAH,BIDR,AUD,DAI,BRL,VAI,USDP}]
            [--export {csv,json,xlsx}] [-h]
```

Get the order book for selected coin

```
optional arguments:
  --vs {USDC,UST,USDT,EUR,GBP,USD}
                        Quote currency (what to view coin vs) (default: USDT)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

![cbbook](https://user-images.githubusercontent.com/46355364/154059918-6d3b17e8-4e33-4e07-9d7d-9826564561b8.png)

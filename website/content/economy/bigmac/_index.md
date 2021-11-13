```
usage: bigmac [-c COUNTRIES] [--raw] [-h] [--export {png,jpg,pdf,svg}]
```

Get historical Big Mac Index [Nasdaq Data Link]

```
optional arguments:
  -c COUNTRIES, --countries COUNTRIES
                        Country codes to get data for. (default: USA)
  --raw                 Show raw data (default: False)
  -h, --help            show this help message (default: False)
  --export {png,jpg,pdf,svg}
                        Export or figure into png, jpg, pdf, svg (default: )
```

Sample usage, which gets the index for 7 different countries:
```
bigmac -c USA,EUR,MEX,CAN,UAE,RUS
```

![BigMac](https://user-images.githubusercontent.com/18151143/141603738-ffa86906-4e1e-48b4-97b8-ed51f1806089.png)

```text
usage: interest [-s START] [-w WORDS] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Plot interest over time of words/sentences versus stock price. [Source: Google]

```
optional arguments:
  -s START, --start START
                        starting date (format YYYY-MM-DD) of interest (default: 2020-03-08)
  -w WORDS, --words WORDS
                        Select multiple sentences/words separated by commas. E.g. COVID,WW3,NFT (default: None)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

![snews](https://user-images.githubusercontent.com/25267873/156584514-33c2cd52-4763-43cd-8a53-4118b8615450.png)

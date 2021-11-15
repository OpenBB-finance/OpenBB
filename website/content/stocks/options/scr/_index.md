```
usage: scr [-p {template,high_IV}] [--export {csv,json,xlsx}] [-n N_SHOW] [-h]
```

Sreener filter output from https://ops.syncretism.io/index.html. Where: CS: Contract Symbol; S: Symbol, T: Option Type; Str: Strike; Exp v: Expiration; IV: Implied Volatility; LP: Last Price; B: Bid; A: Ask; V: Volume; OI: Open Interest; Y: Yield; MY: Monthly Yield; SMP: Regular Market Price; SMDL: Regular Market Day Low; SMDH: Regular Market Day High; LU: Last Trade Date; LC: Last Crawl; ITM: In The Money; PC: Price Change; PB:
Price-to-book.

```
optional arguments:
  -p {template,high_IV}, --preset {template,high_IV}
                        Filter presets (default: template)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -n N_SHOW, --num N_SHOW
                        Number of random entries to show. Default shows all (default: -1)
  -h, --help            show this help message (default: False)
```

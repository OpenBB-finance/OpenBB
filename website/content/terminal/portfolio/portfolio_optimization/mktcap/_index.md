```
usage: property [-p PROPERTY] [-v VALUE] [--pie] [-h]
```

Returns a portfolio that is weighted based on market cap.

```
optional arguments:
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio (default: 1)
  --pie                 Display a pie chart for weights (default: False)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 14, 11:19 (✨) /portfolio/po/ $ mktcap
      Weights
┌────────┬─────────┐
│        │ Value   │
├────────┼─────────┤
│ BNS.TO │ 15.70 % │
├────────┼─────────┤
│ BMO.TO │ 13.48 % │
├────────┼─────────┤
│ TD.TO  │ 27.06 % │
├────────┼─────────┤
│ CM.TO  │ 10.16 % │
├────────┼─────────┤
│ NA.TO  │  4.84 % │
├────────┼─────────┤
│ RY.TO  │ 28.73 % │
└────────┴─────────
```

![mktcap](https://user-images.githubusercontent.com/46355364/153903395-45f4b424-cab3-41ac-91ee-745eddff7e71.png)

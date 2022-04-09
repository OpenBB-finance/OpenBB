```text
usage: dividend [-v VALUE] [--pie] [-h]
```

Returns a portfolio that is weighted for optimaal dividend yield.

```
optional arguments:
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio (default: 1)
  --pie                 Display a pie chart for weights (default: False)
  -h, --help            show this help message (default: False)
```
```
2022 Feb 14, 11:09 (✨) /portfolio/po/ $ select BNS.TO,TD.TO,NA.TO,CM.TO,RY.TO,BMO.TO

2022 Feb 14, 11:09 (✨) /portfolio/po/ $ dividend
      Weights
┌────────┬─────────┐
│        │ Value   │
├────────┼─────────┤
│ BNS.TO │ 19.74 % │
├────────┼─────────┤
│ BMO.TO │ 16.24 % │
├────────┼─────────┤
│ TD.TO  │ 15.18 % │
├────────┼─────────┤
│ CM.TO  │ 18.17 % │
├────────┼─────────┤
│ NA.TO  │ 15.55 % │
├────────┼─────────┤
│ RY.TO  │ 15.09 % │
└────────┴─────────┘
```
```
2022 Feb 14, 11:10 (✨) /portfolio/po/ $ dividend --pie
```
![dividend](https://user-images.githubusercontent.com/46355364/153901511-ded4f3ab-77db-413e-8352-627205dec059.png)

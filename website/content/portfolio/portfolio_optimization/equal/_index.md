```
usage: equal [-v VALUE] [--pie] [-h]
```

Returns an equally weighted portfolio

```
optional arguments:
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio (default: 1)
  --pie                 Display a pie chart for weights (default: False)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 14, 11:15 (✨) /portfolio/po/ $ equal --pie

      Weights
┌────────┬─────────┐
│        │ Value   │
├────────┼─────────┤
│ BNS.TO │ 16.66 % │
├────────┼─────────┤
│ BMO.TO │ 16.66 % │
├────────┼─────────┤
│ TD.TO  │ 16.66 % │
├────────┼─────────┤
│ CM.TO  │ 16.66 % │
├────────┼─────────┤
│ NA.TO  │ 16.66 % │
├────────┼─────────┤
│ RY.TO  │ 16.66 % │
└────────┴─────────┘
```

![equal](https://user-images.githubusercontent.com/46355364/153902518-74f2818f-b844-4b0b-925f-7255898b51f4.png)

```
usage: energy [--export {csv,json,xlsx}] [-h]
```

Today's energy futures overview. Source: (https://finviz.com)

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 04:49 (✨) /economy/ $ energy
                    Future Table
┌─────────────────┬───────────┬───────┬────────────┐
│                 │ prevClose │ last  │ change (%) │
├─────────────────┼───────────┼───────┼────────────┤
│ Ethanol         │ 2.16      │ 2.22  │ 2.78       │
├─────────────────┼───────────┼───────┼────────────┤
│ Gasoline RBOB   │ 2.78      │ 2.72  │ -2.23      │
├─────────────────┼───────────┼───────┼────────────┤
│ Crude Oil Brent │ 96.48     │ 94.15 │ -2.42      │
├─────────────────┼───────────┼───────┼────────────┤
│ Natural Gas     │ 4.20      │ 4.42  │ 5.29       │
├─────────────────┼───────────┼───────┼────────────┤
│ Heating Oil     │ 2.96      │ 2.89  │ -2.46      │
├─────────────────┼───────────┼───────┼────────────┤
│ Crude Oil WTI   │ 95.46     │ 92.84 │ -2.74      │
└─────────────────┴───────────┴───────┴────────────┘
```

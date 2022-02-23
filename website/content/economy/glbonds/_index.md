```
usage: glbonds [--export {csv,json,xlsx}] [-h]
```

An overview of global bonds. [Source: Wall St. Journal]

```
optional arguments:
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 04:58 (✨) /economy/ $ glbonds
                              Global Bonds
┌───────────────────────────────────┬──────────┬─────────┬─────────────┐
│                                   │ Rate (%) │ Yld (%) │ Yld Chg (%) │
├───────────────────────────────────┼──────────┼─────────┼─────────────┤
│ U.S. 10 Year Treasury Note        │ 1.875    │ 2.028   │ 0.039       │
├───────────────────────────────────┼──────────┼─────────┼─────────────┤
│ Germany 10 Year Government Bond   │ 0.000    │ 0.284   │ 0.002       │
├───────────────────────────────────┼──────────┼─────────┼─────────────┤
│ U.K. 10 Year Gilt                 │ 4.750    │ 1.558   │ -0.033      │
├───────────────────────────────────┼──────────┼─────────┼─────────────┤
│ Japan 10 Year Government Bond     │ 0.100    │ 0.216   │ -0.002      │
├───────────────────────────────────┼──────────┼─────────┼─────────────┤
│ Australia 10 Year Government Bond │ 1.000    │ 2.185   │ 0.049       │
├───────────────────────────────────┼──────────┼─────────┼─────────────┤
│ China 10 Year Government Bond     │ 2.890    │ 2.816   │ -0.007      │
└───────────────────────────────────┴──────────┴─────────┴─────────────┘
```

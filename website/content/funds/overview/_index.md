```
usage: overview [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

Show overview of funds from selected country.

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of search results to show (default: 20)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )

```

Sample usage:
```
/fund/ $ overview -l 5
                                                             Fund overview for United States                                                              
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ name                                                ┃ full_name                                    ┃ symbol ┃ last   ┃ change ┃ currency ┃ Assets (1B) ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ Vanguard 500 Index Fund Admiral Shares              │ Vanguard 500 Index Admiral                   │ VFIAX  │ 441.63 │ -0.10% │ USD      │ 435.40      │
├─────────────────────────────────────────────────────┼──────────────────────────────────────────────┼────────┼────────┼────────┼──────────┼─────────────┤
│ Fidelity® 500 Index Fund                            │ Fidelity 500 Index Institutional Prem        │ FXAIX  │ 165.99 │ -0.10% │ USD      │ 380.00      │
├─────────────────────────────────────────────────────┼──────────────────────────────────────────────┼────────┼────────┼────────┼──────────┼─────────────┤
│ Vanguard Total Stock Market Index Fund Admiral      │ Vanguard Total Stock Market Index Admiral    │ VTSAX  │ 117.96 │ -0.22% │ USD      │ 329.59      │
│ Shares                                              │                                              │        │        │        │          │             │
├─────────────────────────────────────────────────────┼──────────────────────────────────────────────┼────────┼────────┼────────┼──────────┼─────────────┤
│ Vanguard Total Stock Market Index Fund              │ Vanguard Total Stock Market Index Instl Plus │ VSMPX  │ 221.26 │ -0.21% │ USD      │ 284.00      │
│ Institutional Plus Shares                           │                                              │        │        │        │          │             │
├─────────────────────────────────────────────────────┼──────────────────────────────────────────────┼────────┼────────┼────────┼──────────┼─────────────┤
│ Vanguard Total Stock Market Index Fund              │ Vanguard Total Stock Market Index I          │ VITSX  │ 117.98 │ -0.21% │ USD      │ 244.37      │
│ Institutional Shares                                │                                              │        │        │        │          │             │
└─────────────────────────────────────────────────────┴──────────────────────────────────────────────┴────────┴────────┴────────┴──────────┴─────────────┘
```
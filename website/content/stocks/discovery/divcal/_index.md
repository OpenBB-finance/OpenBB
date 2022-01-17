```
usage: divcal [-d DATE] [-s SORT [SORT ...]] [-a] [-h] [--export {csv,json,xlsx}] [-l LIMIT]
```
Get dividend calendar for selected date
```
optional arguments:
  -d DATE, --date DATE  Date to get format for (default: 2022-01-14 22:50:41.433203)
  -s SORT [SORT ...], --sort SORT [SORT ...]
                        Column to sort by (default: ['Dividend'])
  -a, --ascend          Flag to sort in ascending order (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 10)
```

```
                                                      Dividend Calendar for 2022-01-14                                                       
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Name                                                ┃ Symbol ┃ Ex-Dividend Date ┃ Payment Date ┃ Record Date ┃ Dividend ┃ Annual Dividend ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ Grupo Aeroportuario del Centro Norte S.A.B. de C.V. │ OMAB   │ 01/14/2022       │ 01/26/2022   │ 01/18/2022  │ 7.77     │ 5.57            │
├─────────────────────────────────────────────────────┼────────┼──────────────────┼──────────────┼─────────────┼──────────┼─────────────────┤
│ PNC Financial Services Group, Inc. (The)            │ PNC    │ 01/14/2022       │ 02/05/2022   │ 01/18/2022  │ 1.25     │ 5.00            │
├─────────────────────────────────────────────────────┼────────┼──────────────────┼──────────────┼─────────────┼──────────┼─────────────────┤
│ Sabine Royalty Trust                                │ SBR    │ 01/14/2022       │ 01/31/2022   │ 01/18/2022  │ 0.88     │ 10.52           │
└─────────────────────────────────────────────────────┴────────┴──────────────────┴──────────────┴─────────────┴──────────┴─────────────────┘

```
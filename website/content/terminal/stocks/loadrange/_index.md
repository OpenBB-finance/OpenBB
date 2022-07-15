```
usage: loadrange [-s START] [-e END] [-h]
```

Changes the data being used by a subset of the loaded data.

It can be used in many /stocks/... path

That can be useful if you want to compare or make a analysis over only the last month or week of a already loaded data without having to load it again from the /stocks/ path and revert back


```
optional arguments:
  -s START, --start START
                        The starting row which you want to slice the data
  -e END, --end END     The final row row which you want to slice the data

  -h, --help            show this help message (default: False)

```


Example:
```
2022 Feb 16, 08:30 (✨) /stocks/qa/ $ raw -l 5

        Raw Data
┏━━━━━━━━━━━━┳━━━━━━━━━┓
┃            ┃ Returns ┃
┡━━━━━━━━━━━━╇━━━━━━━━━┩
│ 2022-07-08 │ -0.007  │
├────────────┼─────────┤
│ 2022-07-11 │ -0.033  │
├────────────┼─────────┤
│ 2022-07-12 │ -0.023  │
├────────────┼─────────┤
│ 2022-07-13 │ 0.011   │
├────────────┼─────────┤
│ 2022-07-14 │ 0.002   │
└────────────┴─────────┘

2022 Feb 16, 08:29 (✨) /stocks/qa/ $ loadrange -e -5

2022 Feb 16, 08:30 (✨) /stocks/qa/ $ raw -l 5

        Raw Data
┏━━━━━━━━━━━━┳━━━━━━━━━┓
┃            ┃ Returns ┃
┡━━━━━━━━━━━━╇━━━━━━━━━┩
│ 2022-06-30 │ -0.025  │
├────────────┼─────────┤
│ 2022-07-01 │ 0.032   │
├────────────┼─────────┤
│ 2022-07-05 │ 0.036   │
├────────────┼─────────┤
│ 2022-07-06 │ 0.007   │
├────────────┼─────────┤
│ 2022-07-07 │ 0.017   │
└────────────┴─────────┘

2022 Feb 16, 08:30 (✨) /stocks/qa/ $ loadfulldata

2022 Feb 16, 08:30 (✨) /stocks/qa/ $ raw -l 5

        Raw Data
┏━━━━━━━━━━━━┳━━━━━━━━━┓
┃            ┃ Returns ┃
┡━━━━━━━━━━━━╇━━━━━━━━━┩
│ 2022-07-08 │ -0.007  │
├────────────┼─────────┤
│ 2022-07-11 │ -0.033  │
├────────────┼─────────┤
│ 2022-07-12 │ -0.023  │
├────────────┼─────────┤
│ 2022-07-13 │ 0.011   │
├────────────┼─────────┤
│ 2022-07-14 │ 0.002   │
└────────────┴─────────┘

```
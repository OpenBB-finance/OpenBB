```
usage: loadfulldata [-h]
```

It reloads the full data after you used loadrange for analyse only part of the loaded data.

The changes made in the /stock/ path affects all paths below.

The changes made in all paths below /stock/ like /stock/dps are lost once you leave the controller.

That is intended to use only a subset in analysis.

```
optional arguments:
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
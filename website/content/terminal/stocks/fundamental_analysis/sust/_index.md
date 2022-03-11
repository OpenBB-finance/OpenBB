```
usage: sust [-h] [--export {csv,json,xlsx}]
```

Print sustainability values of the company. [Source: Yahoo Finance]

```
optional arguments:
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 16, 09:01 (✨) /stocks/fa/ $ sust
         Ticker Sustainability
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃                        ┃ Value       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ Palm oil               │ False       │
├────────────────────────┼─────────────┤
│ Controversial weapons  │ False       │
├────────────────────────┼─────────────┤
│ Gambling               │ False       │
├────────────────────────┼─────────────┤
│ Social score           │ 16.16       │
├────────────────────────┼─────────────┤
│ Nuclear                │ False       │
├────────────────────────┼─────────────┤
│ Fur leather            │ False       │
├────────────────────────┼─────────────┤
│ Alcoholic              │ False       │
├────────────────────────┼─────────────┤
│ Gmo                    │ False       │
├────────────────────────┼─────────────┤
│ Catholic               │ False       │
├────────────────────────┼─────────────┤
│ Social percentile      │ None        │
├────────────────────────┼─────────────┤
│ Peer count             │ 37          │
├────────────────────────┼─────────────┤
│ Governance score       │ 9.61        │
├────────────────────────┼─────────────┤
│ Environment percentile │ None        │
├────────────────────────┼─────────────┤
│ Animal testing         │ False       │
├────────────────────────┼─────────────┤
│ Tobacco                │ False       │
├────────────────────────┼─────────────┤
│ Total esg              │ 28.54       │
├────────────────────────┼─────────────┤
│ Highest controversy    │ 3           │
├────────────────────────┼─────────────┤
│ Esg performance        │ AVG_PERF    │
├────────────────────────┼─────────────┤
│ Coal                   │ False       │
├────────────────────────┼─────────────┤
│ Pesticides             │ False       │
├────────────────────────┼─────────────┤
│ Adult                  │ False       │
├────────────────────────┼─────────────┤
│ Percentile             │ 55.73       │
├────────────────────────┼─────────────┤
│ Peer group             │ Automobiles │
├────────────────────────┼─────────────┤
│ Small arms             │ False       │
├────────────────────────┼─────────────┤
│ Environment score      │ 2.78        │
├────────────────────────┼─────────────┤
│ Governance percentile  │ None        │
├────────────────────────┼─────────────┤
│ Military contract      │ False       │
└────────────────────────┴─────────────┘
```

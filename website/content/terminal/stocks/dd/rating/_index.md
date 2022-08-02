```
usage: rating [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

Based on specific ratios, prints information whether the company is a (strong) buy, neutral or a (strong) sell. The following fields are expected: P/B, ROA, DCF, P/E, ROE, and D/E. [Source: Financial Modeling Prep]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        limit of last days to display ratings
  -h, --help            show this help message
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xls
```

Example (Google):
```
2022 Feb 16, 04:34 (✨) /stocks/dd/ $ rating
                                           Rating
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃            ┃ Rating ┃ DCF        ┃ ROE     ┃ ROA     ┃ DE      ┃ PE         ┃ PB         ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-02-15 │ Buy    │ Strong Buy │ Neutral │ Neutral │ Neutral │ Strong Buy │ Strong Buy │
├────────────┼────────┼────────────┼─────────┼─────────┼─────────┼────────────┼────────────┤
│ 2022-02-14 │ Buy    │ Strong Buy │ Neutral │ Neutral │ Neutral │ Strong Buy │ Strong Buy │
├────────────┼────────┼────────────┼─────────┼─────────┼─────────┼────────────┼────────────┤
│ 2022-02-11 │ Buy    │ Strong Buy │ Neutral │ Neutral │ Neutral │ Strong Buy │ Strong Buy │
├────────────┼────────┼────────────┼─────────┼─────────┼─────────┼────────────┼────────────┤
│ 2022-02-10 │ Buy    │ Strong Buy │ Neutral │ Neutral │ Neutral │ Strong Buy │ Strong Buy │
├────────────┼────────┼────────────┼─────────┼─────────┼─────────┼────────────┼────────────┤
│ 2022-02-09 │ Buy    │ Strong Buy │ Neutral │ Neutral │ Neutral │ Strong Buy │ Strong Buy │
└────────────┴────────┴────────────┴─────────┴─────────┴─────────┴────────────┴────────────┘
```

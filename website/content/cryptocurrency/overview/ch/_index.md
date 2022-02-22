```
usage: ch [-l N] [-s {Platform,Date,Amount [$],Audit,Slug,URL}] [--descend] [-h] [--export {csv,json,xlsx}]
```

Display list of major crypto-related hacks [Source: https://rekt.news]
Can be sorted by {Platform,Date,Amount [$],Audit,Slug,URL} with --sort and reverse the display order with --descend
Show only N elements with --limit N
Accepts --slug or -s to check individual crypto hack (e.g., -s polynetwork-rekt)

```
optional arguments:
  -s SLUG, --slug SLUG  Rekt news slug to check (e.g., polynetwork-rekt)
  -l N, --limit N       display N number records (default: 15)
  --sort {Platform,Date,Amount [$],Audit,Slug,URL}
                        Sort by given column. Default: Amount [$]
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 08:16 (✨) /crypto/ov/ $ ch
                                                            Major Crypto Hacks
┌────────────────────────┬────────────┬────────────┬────────────────────────┬────────────────────┬───────────────────────────────────────┐
│ Platform               │ Date       │ Amount [$] │ Audit                  │ Slug               │ URL                                   │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ Poly Network - REKT    │ 2021-08-10 │ 611 M      │ Unaudited              │ polynetwork-rekt   │ https://rekt.news/polynetwork-rekt/   │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ Wormhole - REKT        │ 2022-02-02 │ 326 M      │ Neodyme                │ wormhole-rekt      │ https://rekt.news/wormhole-rekt/      │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ BitMart - REKT         │ 2021-12-04 │ 196 M      │ N/A                    │ bitmart-rekt       │ https://rekt.news/bitmart-rekt/       │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ Compound - REKT        │ 2021-09-29 │ 147 M      │ Unaudited              │ compound-rekt      │ https://rekt.news/compound-rekt/      │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ Vulcan Forged - REKT   │ 2021-12-13 │ 140 M      │ Unaudited              │ vulcan-forged-rekt │ https://rekt.news/vulcan-forged-rekt/ │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ Cream Finance - REKT 2 │ 2021-10-27 │ 130 M      │ Unaudited              │ cream-rekt-2       │ https://rekt.news/cream-rekt-2/       │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ Badger - REKT          │ 2021-12-02 │ 120 M      │ Unaudited              │ badger-rekt        │ https://rekt.news/badger-rekt/        │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ Qubit Finance - REKT   │ 2022-01-28 │ 80 M       │ Unaudited              │ qubit-rekt         │ https://rekt.news/qubit-rekt/         │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ Ascendex - REKT        │ 2021-12-12 │ 77.700 M   │ Unaudited              │ ascendex-rekt      │ https://rekt.news/ascendex-rekt/      │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ EasyFi - REKT          │ 2021-04-19 │ 59 M       │ Unaudited              │ easyfi-rekt        │ https://rekt.news/easyfi-rekt/        │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ Uranium Finance - REKT │ 2021-04-28 │ 57.200 M   │ Unaudited              │ uranium-rekt       │ https://rekt.news/uranium-rekt/       │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ bZx - REKT             │ 2021-11-05 │ 55 M       │ Unaudited              │ bzx-rekt           │ https://rekt.news/bzx-rekt/           │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ PancakeBunny - REKT    │ 2021-05-19 │ 45 M       │ Unaudited              │ pancakebunny-rekt  │ https://rekt.news/pancakebunny-rekt/  │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ Kucoin - REKT          │ 2020-09-29 │ 45 M       │ Internal audit         │ epic-hack-homie    │ https://rekt.news/epic-hack-homie/    │
├────────────────────────┼────────────┼────────────┼────────────────────────┼────────────────────┼───────────────────────────────────────┤
│ Alpha Finance - REKT   │ 2021-02-13 │ 37.500 M   │ Quantstamp, Peckshield │ alpha-finance-rekt │ https://rekt.news/alpha-finance-rekt/ │
└────────────────────────┴────────────┴────────────┴────────────────────────┴────────────────────┴───────────────────────────────────────┘
```

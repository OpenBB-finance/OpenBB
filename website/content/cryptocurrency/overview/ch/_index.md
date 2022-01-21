```
usage: ch [-l N] [-s {Platform,Date,Amount [$],Audit,Slug,URL}] [--descend] [-h] [--export {csv,json,xlsx}]

Display list of major crypto-related hacks [Source: https://rekt.news]
Can be sorted by {Platform,Date,Amount [$],Audit,Slug,URL} with --sort and reverse the display order with --descend
Show only N elements with --limit N
Accepts --slug or -s to check individual crypto hack (e.g., -s polynetwork-rekt)

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

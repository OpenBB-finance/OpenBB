```
usage: dev [--export {csv,json,xlsx}] [-h]
```

Developers data for loaded coin. If the development data is available you can see how the code development of given coin is going on. There are some statistics that shows number of stars, forks, subscribers, pull requests, commits, merges, contributors on github.

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 07:13 (✨) /crypto/dd/ $ dev
   Developers Data for Loaded Coin
┌───────────────────────────┬───────┐
│ Metric                    │ Value │
├───────────────────────────┼───────┤
│ Forks                     │ 31593 │
├───────────────────────────┼───────┤
│ Stars                     │ 61894 │
├───────────────────────────┼───────┤
│ Subscribers               │ 3904  │
├───────────────────────────┼───────┤
│ Total Issues              │ 6729  │
├───────────────────────────┼───────┤
│ Closed Issues             │ 6114  │
├───────────────────────────┼───────┤
│ Pull Requests Merged      │ 9418  │
├───────────────────────────┼───────┤
│ Pull Request Contributors │ 771   │
├───────────────────────────┼───────┤
│ Commit Count 4 Weeks      │ 266   │
└───────────────────────────┴───────┘
```

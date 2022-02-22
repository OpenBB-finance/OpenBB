```
usage: web [--export {csv,json,xlsx}] [-h]
```

Websites found for given Coin. You can find there urls to homepage, forum, announcement site and others.

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 07:49 (✨) /crypto/dd/ $ web
            Websites for Loaded Coin
┌────────────────────┬──────────────────────────┐
│ Metric             │ Value                    │
├────────────────────┼──────────────────────────┤
│ Homepage           │ http://www.bitcoin.org   │
├────────────────────┼──────────────────────────┤
│ Official Forum Url │ https://bitcointalk.org/ │
├────────────────────┼──────────────────────────┤
│ Announcement Url   │                          │
└────────────────────┴──────────────────────────┘
```


```
usage: events [-c {NZ,AU,ERL,CA,EU,US,JP,CN,GB,CH}] [-n NUM] [-i {low,medium,high,all}] [--export {csv,json,xlsx}] [-h]
```

Output economy impact calendar impact events. Note that this is a premium feature from the Finnhub API.

```
optional arguments:
  -c {NZ,AU,ERL,CA,EU,US,JP,CN,GB,CH}, --country {NZ,AU,ERL,CA,EU,US,JP,CN,GB,CH}
                        Country from where to get economy calendar impact events (default: US)
  -n NUM, --num NUM     Number economy calendar impact events to display (default: 10)
  -i {low,medium,high,all}, --impact {low,medium,high,all}
                        Impact of the economy event (default: all)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

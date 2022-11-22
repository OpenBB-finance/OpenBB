```
usage: vwap [-o N_OFFSET] [--export {csv,json,xlsx}] [-h]
```

The Volume Weighted Average Price that measures the average typical price by volume. It is typically used with intraday charts to identify general
direction.

```
optional arguments:
  -o N_OFFSET, --offset N_OFFSET
                        offset (default: 0)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:

```
2022 Feb 16, 11:36 (🦋) /stocks/ta/ $ load GOOGL -i 1

Loading Intraday 1min GOOGL stock with starting period 2022-02-10 for analysis.

Datetime: 2022 Feb 16 11:36
Timezone: America/New_York
Currency: USD
Market:   CLOSED

2022 Feb 16, 11:36 (🦋) /stocks/ta/ $ vwap
```

![vwap](https://user-images.githubusercontent.com/46355364/154312502-9377c57c-6e34-42a6-b021-674e7d4561dd.png)

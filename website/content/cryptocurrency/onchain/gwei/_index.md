```
usage: onchain [--export {csv,json,xlsx}] [-h]
```

Display ETH gas fees [Source: https://ethgasstation.info]

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example output:

| Tx Type | Fee (gwei) | Duration (min) |
| ------- | ---------- | -------------- |
| Fastest | 108        | 0.4            |
| Fast    | 95         | 0.5            |
| Average | 72         | 4.0            |
| Slow    | 68         | 11.9           |

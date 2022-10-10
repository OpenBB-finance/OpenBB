```
usage: export [-t {csv,xlsx}] [-d {}] [-h]
```

Export dataset to Excel

```
optional arguments:
  -t {csv,xlsx}, --type {csv,xlsx}
                        The file type you wish to export to (default: xlsx)
  -d {}, --target-dataset {}
                        The name of the dataset you want to select (default: None)
  -h, --help            show this help message (default: False)

For more information and examples, use 'about export' to access the related guide.
```

Example:
```
(🦋) /forecast/ $ load aapl

(🦋) /forecast/ $ ema aapl
Successfully added 'EMA_10' to 'aapl' dataset

(🦋) /forecast/ $ export aapl
Saved file: .../OpenBBTerminal/exports/forecast/aapl_20220711_151219.xlsx
```

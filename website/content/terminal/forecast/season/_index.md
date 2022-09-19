```
usage: season [-v VALUES] [-m M] [--max_lag MAX_LAG] [-a ALPHA] [-h] [--export EXPORT]
```

Plot the seasonality for a given column

```
optional arguments:
  -v VALUES, --values VALUES
                        Dataset.column values to be displayed in a plot (default: None)
  -m M                  A time lag to highlight on the plot (default: None)
  --max_lag MAX_LAG     The maximal lag order to consider (default: 24)
  -a ALPHA, --alpha ALPHA
                        The confidence interval to display (default: 0.05)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )

For more information and examples, use 'about season' to access the related guide.
```

Example:
```
(🦋) /forecast/ $ load TSLA.csv

(🦋) /forecast/ $ season TSLA.volume
TODO: screen shot

```

```
usage: plot [-v VALUES] [-h] [--export EXPORT]
```

Plot data based on the index.

```
optional arguments:
  -v VALUES, --values VALUES
                        Dataset.column values to be displayed in a plot (default: None)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )

```

Example:
```
(🦋) /forecast/ $ load aapl.csv

(🦋) /forecast/ $ plot appl.close
```
![close](TODO)

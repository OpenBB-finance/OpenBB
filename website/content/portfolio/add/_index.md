```
usage: load [-n NAME] [-t {stock,bond,option,crypto}] [-v VOLUME] [-d DATE] [-p PRICE] [-f FEES]
            [-r PREMIUM] [--sell] [-h]
```

Add an asset to the current portfolio

```
optional arguments:
  -n, NAME --name NAME  the name of the asset
  -t, --type            the type of asset
  -v, --volume          the amount of the asset
  -d, --date            the date the transaction occurred
  -p, --price           the price of the asset (per unit)
  -f, --fees            the fees paid for the transaction (total)
  -r, --premium         the premium paid/received for the asset
  --sell                the asset was sold (shorted)
  -h, --help            show this help message
```

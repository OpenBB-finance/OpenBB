```
usage: add [-n NAME] [-t {stock,bond,option,crypto,cash}] [-q QUANTITY] [-d DATE] [-p PRICE] [-f FEES]
            [-r PREMIUM] [-a {buy,sell,interest,deposit,withdrawal}] [-h]
```

Add an asset to the current portfolio

```
optional arguments:
  -n, NAME --name NAME  the name of the asset
  -t, --type            the type of asset
  -q, --quantity        the quantity of the asset
  -d, --date            the date the transaction occurred
  -p, --price           the price of the asset (per unit)
  -f, --fees            the fees paid for the transaction (total)
  -r, --premium         the premium paid/received for the asset
  -a, --action          select what you did in the transaction
  -h, --help            show this help message
```

```text
usage: is [-h]
```

See all income statement metrics available [source: StockAnalysis]

```
optional arguments:
  -h, --help  show this help message (default: False)
```
The current list of available options is:

        re           revenue
        cr           cost of revenue
        gp           gross profit (re - cr)
        sga          selling, general and administrative
        rd           research & development
        ooe          other operating expenses
        oi           operating income (gp - sga - rd - ooe)
        ie           interest expense / income
        oe           other expenses / income
        it           income tax
        ni           net income (oi - ie - oe - it)
        pd           preferred dividends
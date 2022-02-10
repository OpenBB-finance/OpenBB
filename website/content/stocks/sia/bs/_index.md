```text
usage: bs [-h]
```

See all balance sheet statement metrics available [source: StockAnalysis]

```
optional arguments:
  -h, --help  show this help message (default: False)
```
The current list of available options is:

        ce            cash & equivalents
        sti           short-term investments
        cce           cash & cash equivalents (ce + sti)
        rec           receivables
        inv           inventory
        oca           other current assets
        tca           total current assets (rec + inv + oca)
        ppe           property, plant & equipment
        lti           long-term investments
        gai           goodwill and intangibles
        olta          other long-term assets
        tlta          total long-term assets (lti + gai + olta)
        ta            total assets (tca + tlta)
        ap            accounts payable
        dr            deferred revenue
        cd            current debt
        ocl           other current liabilities
        tcl           total current liabilities (ac + dr + cd + ocl + tcl)
        ltd           long-term debt
        oltl          other long-term liabilities
        tltl          total long-term liabilities (ltd + oltl)
        tl            total liabilities (tltl + tcl)
        ret           retained earnings
        ci            comprehensive income
        se            stakeholders' equity
        tle           total liabilities and equity (tl + re + ci + se)
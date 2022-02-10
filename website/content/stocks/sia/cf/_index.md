```text
usage: cf [-h]
```

See all cash flow statement metrics available [source: StockAnalysis]

```
optional arguments:
  -h, --help  show this help message (default: False)
```
The current list of available options is:

        ninc         net income
        da           depreciation & amortization
        sbc          share-based compensation
        ooa          other operating activities
        ocf          operating cashflow (ni + da + sbc + ooa)
        cex          cash expenditures
        acq          acquisitions
        cii          change in investments
        oia          other investing activities
        icf          investing cashflow (cex + acq + cii + oia)
        dp           dividends paid
        si           share issuance / repurchase
        di           debt issued / paid
        ofa          other financing activities
        fcf          financing cashflow (dp + si + di + ofa)
        ncf          net cashflow (ocf + icf + fcf)
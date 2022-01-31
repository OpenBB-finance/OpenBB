```
usage: var [-m] [-a] [-p PERCENTILE] [-h]
```

Provides value at risk (short: VaR) of the selected stock.

```
optional arguments:
  -m, --mean            If one should use the mean of the stocks return
  -a, --adjusted        If the VaR should be adjusted for skew and kurtosis (Cornish-Fisher-Expansion)
  -p PERCENTILE, --percent PERCENTILE 
                        Percentile used for VaR calculations, for example input 99.9 equals a 99.9% VaR
  -h, --help            show this help message (default: False)
```

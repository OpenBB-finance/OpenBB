```
usage: file -f FILE [FILE ...] [-h]
```

Select parameter file to use.

Optional arguments:
```
optional arguments:
  -f FILE [FILE ...], --file FILE [FILE ...]
                        Parameter file to be used (default: None)
  -h, --help            show this help message (default: False)
```

```
2022 May 02, 06:51 (🦋) /portfolio/po/ $ file OpenBB_Parameters_Template v1.0.0.xlsx
Parameters:
    historic_period         : 3y
    log_returns             : 0
    return_frequency        : d
    max_nan                 : 0.05
    threshold_value         : 0.3
    nan_fill_method         : time
    risk_free               : 0.003
    significance_level      : 0.05
    risk_measure            : MV
    target_return           : -1
    target_risk             : -1
    expected_return         : hist
    covariance              : hist
    smoothing_factor_ewma   : 0.94
    long_allocation         : 1
    short_allocation        : 0
```
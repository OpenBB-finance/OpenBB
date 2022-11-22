```
usage: arg [-a ARGUMENT ARGUMENT] [-s] [-h]
```

Set a different value for one of the available arguments.

```
optional arguments:
  -a ARGUMENT ARGUMENT, --argument ARGUMENT ARGUMENT
                        Set a value for an argument (default: None)
  -s, --show_arguments  Show the available arguments, the options and a description. (default: False)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 May 02, 05:53 (🦋) /portfolio/po/params/ $ arg historic_period 10y

2022 May 02, 05:53 (🦋) /portfolio/po/params/ $ ?
╭──────────────────────────────────────────────────────────────────────────────────────────── Portfolio - Portfolio Optimization - Parameters ────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                                                                         │
│ Portfolio Risk Parameters (.ini or .xlsx)                                                                                                                                                                                               │
│                                                                                                                                                                                                                                         │
│ Loaded file: OpenBB_Parameters_Template v1.0.0.xlsx                                                                                                                                                                                     │
│                                                                                                                                                                                                                                         │
│     file          load portfolio risk parameters                                                                                                                                                                                        │
│     save          save portfolio risk parameters to specified file                                                                                                                                                                      │
│                                                                                                                                                                                                                                         │
│ Model of interest: maxdecorr                                                                                                                                                                                                            │
│                                                                                                                                                                                                                                         │
│     clear         clear model of interest from filtered parameters                                                                                                                                                                      │
│     set           set model of interest to filter parameters                                                                                                                                                                            │
│     arg           set a different value for an argument                                                                                                                                                                                 │
│                                                                                                                                                                                                                                         │
│ Parameters:                                                                                                                                                                                                                             │
│     historic_period         : 10y                                                                                                                                                                                                       │
│     log_returns             : 0                                                                                                                                                                                                         │
│     return_frequency        : d                                                                                                                                                                                                         │
│     max_nan                 : 0.05                                                                                                                                                                                                      │
│     threshold_value         : 0.3                                                                                                                                                                                                       │
│     nan_fill_method         : time                                                                                                                                                                                                      │
│     risk_free               : 0.003                                                                                                                                                                                                     │
│     significance_level      : 0.05                                                                                                                                                                                                      │
│     covariance              : hist                                                                                                                                                                                                      │
│     long_allocation         : 1                                                                                                                                                                                                         │
│                                                                                                                                                                                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── OpenBB Terminal ─╯
```
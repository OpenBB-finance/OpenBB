```txt
usage: treasury [-m MATURITY [MATURITY ...]] [-sm] [--freq {annually,monthly,weekly,daily}] [-t {nominal,inflation,average,secondary} [{nominal,inflation,average,secondary} ...]] [-s START_DATE] [-e END_DATE] [-st] [-h]
                [--export {csv,json,xlsx}] [--raw] [-l LIMIT]
```

Obtain any set of U.S. treasuries and plot them together. These can be a range of maturities for nominal, inflation-adjusted (on long term average of inflation adjusted) and secondary markets over a lengthy period. Note: 3-month and
10-year treasury yields for other countries are available via the command 'macro' and parameter 'M3YD' and 'Y10YD'. [Source: EconDB / FED]

```txt
optional arguments:
  -m MATURITY [MATURITY ...], --maturity MATURITY [MATURITY ...]
                        The preferred maturity which is dependent on the type of the treasury (default: ['1y'])
  -sm, --show_maturities
                        Show the maturities available for every instrument. (default: False)
  --freq {annually,monthly,weekly,daily}
                        The frequency, this can be annually, monthly, weekly or daily (default: monthly)
  -t {nominal,inflation,average,secondary} [{nominal,inflation,average,secondary} ...], --type {nominal,inflation,average,secondary} [{nominal,inflation,average,secondary} ...]
                        Whether to select nominal, inflation indexed, average inflation indexed or secondary market treasury rates (default: ['nominal'])
  -s START_DATE, --start_date START_DATE
                        The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31) (default: 1934-01-31)
  -e END_DATE, --end_date END_DATE
                        The end date of the data (format: YEAR-DAY-MONTH, i.e. 2021-06-02) (default: 2022-03-15)
  -st, --store          Store the data to be used for plotting with the 'plot' command. (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
  --raw                 Flag to display raw data (default: False)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 10)
```

Example:

```
2022 Mar 15, 07:33 (🦋) /economy/ $ treasury -sm
               Maturity options per instrument
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Instrument ┃ Maturities                                    ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ nominal    │ 1m, 3m, 6m, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y │
├────────────┼───────────────────────────────────────────────┤
│ inflation  │ 5y, 7y, 10y, 20y, 30y                         │
├────────────┼───────────────────────────────────────────────┤
│ average    │ Defined by function                           │
├────────────┼───────────────────────────────────────────────┤
│ secondary  │ 4w, 3m, 6m, 1y                                │
└────────────┴───────────────────────────────────────────────┘
```

```txt
2022 Mar 15, 07:33 (🦋) /economy/ $ treasury -m 1y,3y,5y,10y,30y
```

![3y 5y 10y 30y nominal](https://user-images.githubusercontent.com/46355364/158575884-8ec4e1dc-fb5b-4440-be4b-5e1dcd6d2a5e.png)

```txt
2022 Mar 15, 07:35 (🦋) /economy/ $ treasury -m 5y -t nominal,inflation,average -s 2005-01-01
```

![5y nominal inflation average](https://user-images.githubusercontent.com/46355364/158575921-ff7c387c-8eb6-4716-80c4-f4c5121633f2.png)

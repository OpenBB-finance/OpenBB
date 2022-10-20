```
usage: events [-c COUNTRY [COUNTRY ...]] [-i {high,medium,low,all}] [--cat {employment,credit,balance,economic_activity,central_banks,bonds,inflation,confidence_index}]
              [-s START_DATE] [-e END_DATE] [-h] [--export EXPORT] [--raw] [-l LIMIT]
```
Economic calendar. If no start or end dates, default is the current day high importance events.

```
optional arguments:
  -c COUNTRY [COUNTRY ...], --country COUNTRY [COUNTRY ...]
                        Display calendar for specific country. (default: united states)
  -i {high,medium,low,all}, --importances {high,medium,low,all}
                        Event importance classified as high, medium, low or all. (default: all)
  -cat {employment,credit,balance,economic activity,central banks,bonds,inflation,confidence index} [{employment,credit,balance,economic activity,central banks,bonds,inflation,confidence index} ...], --categories {employment,credit,balance,economic activity,central banks,bonds,inflation,confidence index} [{employment,credit,balance,economic activity,central banks,bonds,inflation,confidence index} ...]
                        Event category. (default: None)
  -s START_DATE, --start_date START_DATE
                        The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31) (default: None)
  -e END_DATE, --end_date END_DATE
                        The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31) (default: None)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --raw                 Flag to display raw data (default: False)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 100)  
```

Example:
```
2022 Aug 08, 09:41 (🦋) /economy/ $ events -c united states -i medium --cat inflation -s 2022-06-15 -e 2022-07-01

                                   United States economic calendar (GMT +1:00)
┏━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┓
┃ Date       ┃ Time  ┃ Currency ┃ Importance ┃ Event                             ┃ Actual ┃ Forecast ┃ Previous ┃
┡━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━┩
│ 2022-06-15 │ 14:30 │ USD      │ Medium     │ Export Price Index (MoM)  (May)   │ 2.8%   │ 1.3%     │ 0.8%     │
├────────────┼───────┼──────────┼────────────┼───────────────────────────────────┼────────┼──────────┼──────────┤
│ 2022-06-15 │ 14:30 │ USD      │ Medium     │ Import Price Index (MoM)  (May)   │ 0.6%   │ 1.1%     │ 0.4%     │
├────────────┼───────┼──────────┼────────────┼───────────────────────────────────┼────────┼──────────┼──────────┤
│ 2022-06-29 │ 14:30 │ USD      │ Medium     │ GDP Price Index (QoQ)  (Q1)       │ 8.3%   │ 8.1%     │ 8.1%     │
├────────────┼───────┼──────────┼────────────┼───────────────────────────────────┼────────┼──────────┼──────────┤
│ 2022-06-30 │ 14:30 │ USD      │ Medium     │ Core PCE Price Index (YoY)  (May) │ 4.7%   │ 4.8%     │ 4.9%     │
├────────────┼───────┼──────────┼────────────┼───────────────────────────────────┼────────┼──────────┼──────────┤
│ 2022-06-30 │ 14:30 │ USD      │ Medium     │ PCE Price index (YoY)  (May)      │ 6.3    │          │ 6.3      │
├────────────┼───────┼──────────┼────────────┼───────────────────────────────────┼────────┼──────────┼──────────┤
│ 2022-06-30 │ 14:30 │ USD      │ Medium     │ PCE price index (MoM)  (May)      │ 0.6%   │          │ 0.2%     │
└────────────┴───────┴──────────┴────────────┴───────────────────────────────────┴────────┴──────────┴──────────┘
```

```
usage: events [-l N] [-s {date,date_to,name,description,is_conference}] [--descend] [-u] [--export {csv,json,xlsx}] [-h]
```

Show information about most important coins events. Most of coins doesn't have any events. You can display only N number of events with --limit
parameter. You can sort data by id, date , date_to, name, description, is_conference --sort parameter and also with --descend flag to sort
descending. You can use additional flag --urls to see urls for each event Displays: date , date_to, name, description, is_conference, link,
proof_image_link

```
optional arguments:
  -l N, --limit N       Limit of records (default: 10)
  -s {date,date_to,name,description,is_conference}, --sort {date,date_to,name,description,is_conference}
                        Sort by given column. Default: date (default: date)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -u, --urls            Flag to show urls. If you will use that flag you will see only date, name, link columns (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 07:14 (✨) /crypto/dd/ $ events
                                                                                          All Events
┌────────────┬────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────┬───────────────┐
│ date       │ date_to    │ name                                                                                                   │ description                             │ is_conference │
├────────────┼────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────┼───────────────┤
│ 2021-06-11 │ None       │ Ask El Salvador for advice: Cuba suspends dollar cash deposits in banks due to US sanctions            │                                         │ False         │
│ 00:00:00   │            │                                                                                                        │                                         │               │
├────────────┼────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────┼───────────────┤
│ 2021-06-11 │ None       │ One of the Richest Bitcoin Whales in History Bought $138,000,000 in BTC Amid Market Turmoil – AronBoss │                                         │ False         │
│ 00:00:00   │            │                                                                                                        │                                         │               │
├────────────┼────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────┼───────────────┤
│ 2021-05-10 │ None       │ Bitcoin’s upcoming Taproot upgrade and why it matters for the network                                  │                                         │ False         │
│ 00:00:00   │            │                                                                                                        │                                         │               │
├────────────┼────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────┼───────────────┤
│ 2021-03-24 │ 2021-03-26 │ THE CRYPTO GATHERING                                                                                   │                                         │ False         │
│ 08:00:00   │ 23:00:00   │                                                                                                        │                                         │               │
├────────────┼────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────┼───────────────┤
│ 2018-10-09 │ 2018-10-09 │ Blockchain & Bitcoin Conference Switzerland                                                            │ The second conference organized by      │ True          │
│ 09:00:00   │ 18:00:00   │                                                                                                        │ Smile-Expo company in Geneva, the       │               │
│            │            │                                                                                                        │ European fintech hub. The conference    │               │
│            │            │                                                                                                        │ will also feature the demozone.         │               │
├────────────┼────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────┼───────────────┤
│ 2018-09-28 │ 2018-09-30 │ Super Conference                                                                                       │ KWIC, Kitchener - Waterloo, ON, Canada. │ True          │
│ 20:00:00   │ 16:00:00   │                                                                                                        │ 29 September, 2018                      │               │
├────────────┼────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────┼───────────────┤
│ 2018-07-10 │ None       │ SEC- ETF VanEck decision                                                                               │                                         │ False         │
│ 12:00:00   │            │                                                                                                        │                                         │               │
└────────────┴────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────┴─────────────────────────────────────────┴───────────────┘
```

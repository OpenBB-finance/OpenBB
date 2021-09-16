```
usage: events [-t TOP] [-s {date,date_to,name,description,is_conference}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]
```

Show information about most important coins events. Most of coins doesn't have any events. You can display only top N number of events with --top
parameter. You can sort data by id, date , date_to, name, description, is_conference --sort parameter and also with --descend flag to sort
descending. You can use additional flag --links to see urls for each event Displays: date , date_to, name, description, is_conference, link,
proof_image_link

```
optional arguments:
  -t TOP, --top TOP     Limit of records (default: 10)
  -s {date,date_to,name,description,is_conference}, --sort {date,date_to,name,description,is_conference}
                        Sort by given column. Default: date (default: date)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -l, --links           Flag to show urls. If you will use that flag you will see only date, name, link columns (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

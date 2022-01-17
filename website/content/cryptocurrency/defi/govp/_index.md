```
usage: govp [-l LIMIT] [-s {submitTime,id,depositEndTime,status,type,title,Yes,No}] [--status {voting,deposit,passed,rejected,all}] [--descend] [-h] [--export {csv,json,xlsx}]
```
Displays terra blockchain governance proposals list. [Source: https://fcd.terra.dev/swagger]
```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of proposals to show (default: 10)
  -s {submitTime,id,depositEndTime,status,type,title,Yes,No}, --sort {submitTime,id,depositEndTime,status,type,title,Yes,No}
                        Sort by given column. Default: id (default: id)
  --status {voting,deposit,passed,rejected,all}
                        Status of proposal. Default: all (default: all)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```
```
usage: cpsearch [-q QUERY] [-c {currencies,exchanges,icos,people,tags,all}] [-t TOP] [-s {category,id,name}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Search over CoinPaprika API You can display only top N number of results with --top parameter. You can sort data by id, name , category --sort
parameter and also with --descend flag to sort descending. To choose category in which you are searching for use --cat/-c parameter. Available
categories: currencies|exchanges|icos|people|tags|all Displays: id, name, category

```
optional arguments:
  -q QUERY, --query QUERY
                        phrase for search (default: None)
  -c {currencies,exchanges,icos,people,tags,all}, --cat {currencies,exchanges,icos,people,tags,all}
                        Categories to search: currencies|exchanges|icos|people|tags|all. Default: all (default: all)
  -t TOP, --top TOP     Limit of records (default: 10)
  -s {category,id,name}, --sort {category,id,name}
                        Sort by given column. Default: id (default: id)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

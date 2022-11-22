---
title: search
description: OpenBB Terminal Function
---

# search

Search over CoinPaprika API You can display only N number of results with --limit parameter. You can sort data by id, name , category --sort parameter and also with --reverse flag to sort descending. To choose category in which you are searching for use --cat/-c parameter. Available categories: currencies|exchanges|icos|people|tags|all Displays: id, name, category

### Usage

```python
usage: search -q QUERY [QUERY ...] [-c {currencies,exchanges,icos,people,tags,all}] [-l LIMIT] [-s {category,id,name}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| query | phrase for search | None | False | None |
| category | Categories to search: currencies|exchanges|icos|people|tags|all. Default: all | all | True | currencies, exchanges, icos, people, tags, all |
| limit | Limit of records | 10 | True | None |
| sortby | Sort by given column. Default: id | id | True | category, id, name |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
---


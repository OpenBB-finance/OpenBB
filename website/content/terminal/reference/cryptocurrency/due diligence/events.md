---
title: events
description: OpenBB Terminal Function
---

# events

Show information about most important coins events. Most of coins doesn't have any events. You can display only top N number of events with --limit parameter. You can sort data by id, date , date_to, name, description, is_conference --sort parameter and also with --reverse flag to sort ascending. You can use additional flag --urls to see urls for each event Displays: date , date_to, name, description, is_conference, link, proof_image_link

### Usage

```python
usage: events [-l LIMIT] [-s {date,date_to,name,description,is_conference}] [-r] [-u]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of records | 10 | True | None |
| sortby | Sort by given column. Default: date | date | True | date, date_to, name, description, is_conference |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| urls | Flag to show urls. If you will use that flag you will see only date, name, link columns | False | True | None |
---


---
title: lcsc
description: OpenBB Terminal Function
---

# lcsc

Display Luna circulating supply changes stats. [Source: Smartstake.io] Follow these steps to get the key token: 1. Head to https://terra.smartstake.io/ 2. Right click on your browser and choose Inspect 3. Select Network tab (by clicking on the expand button next to Source tab) 4. Go to Fetch/XHR tab, and refresh the page 5. Get the option looks similar to the following: `listData?type=history&dayCount=30` 6. Extract the key and token out of the URL

### Usage

```python
lcsc [-d DAYS]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| days | Number of days to display. Default: 30 days | 30 | True | range(1, 1000) |

---

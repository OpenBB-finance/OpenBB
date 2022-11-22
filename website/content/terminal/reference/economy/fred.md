---
title: fred
description: OpenBB Terminal Function
---

# fred

Query the FRED database and plot data based on the Series ID. [Source: FRED]

### Usage

```python
usage: fred [-p PARAMETER] [-s START_DATE] [-e END_DATE] [-q QUERY]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| parameter | Series ID of the Macro Economic data from FRED |  | True | None |
| start_date | Starting date (YYYY-MM-DD) of data | None | True | None |
| end_date | Ending date (YYYY-MM-DD) of data | None | True | None |
| query | Query the FRED database to obtain Series IDs given the query search term. | None | True | None |
---


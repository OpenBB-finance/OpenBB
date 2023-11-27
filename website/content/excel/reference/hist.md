---
title: OBB.HIST
description: ok
keywords:
- dividend calendar
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get historical data by providing symbol and field tag.

```excel wordwrap
=OBB.HIST(symbol; field; [start_date]; [end_date]; [period])
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Text | Symbol to get data for, e.g. 'AAPL'. | None | False |
| field | Text | Field to get data for, e.g. 'ebitda'. | None | False |
| start_date | Text | Start date of the data, in YYYY-MM-DD format, defaults to 5 years ago. | None | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format, defaults to today. | None | True |
| period | Text | Time period of the data to return, can be 'annual' or 'quarter', defaults to 'annual'. | annual | True |

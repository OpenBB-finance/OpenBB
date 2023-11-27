---
title: OBB.LAST
description: ok
keywords:
- dividend calendar
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get latest data point by providing symbol and field tag.

```excel wordwrap
=OBB.LAST(symbol; field; [provider])
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Text | Symbol to get data for, e.g. 'AAPL'. | None | False |
| field | Text | Field to get data for, e.g. 'ebitda'. | None | False |
| period | Text | Time period of the data to return, can be 'annual' or 'quarter', defaults to 'annual'. | annual | True |

---
title: ichimoku
description: The Ichimoku Cloud, also known as Ichimoku Kinko Hyo, is a versatile indicator that defines support and resistance, identifies trend direction, gauges momentum and provides trading signals
keywords:
- stocks.ta
- ichimoku
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /ta/ichimoku - Reference | OpenBB Terminal Docs" />

The Ichimoku Cloud, also known as Ichimoku Kinko Hyo, is a versatile indicator that defines support and resistance, identifies trend direction, gauges momentum and provides trading signals. Ichimoku Kinko Hyo translates into "one look equilibrium chart". With one look, chartists can identify the trend and look for potential signals within that trend.

### Usage

```python wordwrap
ichimoku [-c N_CONVERSION] [-b N_BASE] [-l N_LAGGING] [-f N_FORWARD]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| n_conversion | -c  --conversion | conversion line period | 9 | True | None |
| n_base | -b  --base | base line period | 26 | True | None |
| n_lagging | -l  --lagging | lagging span period | 52 | True | None |
| n_forward | -f  --forward | forward span period | 26 | True | None |

---

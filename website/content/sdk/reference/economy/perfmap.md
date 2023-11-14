---
title: perfmap
description: This is the documentation page of perfmap, a tool that opens Finviz performance
  map in the browser. It supports various performance periods and map filters.
keywords:
- Finviz
- performance map
- economy model
- SP500
- ETF
- world map
- perfmap
- period
- map filter
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.perfmap - Reference | OpenBB SDK Docs" />

Opens Finviz map website in a browser. [Source: Finviz]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/finviz_model.py#L42)]

```python
openbb.economy.perfmap(period: str = "1d", map_filter: str = "sp500")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| period | str | Performance period. Available periods are 1d, 1w, 1m, 3m, 6m, 1y. | 1d | True |
| scope | str | Map filter. Available map filters are sp500, world, full, etf. | None | True |


---

## Returns

This function does not return anything

---

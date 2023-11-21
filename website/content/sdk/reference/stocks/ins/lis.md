---
title: lis
description: Get latest insider sales
keywords:
- stocks
- ins
- lis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ins.lis - Reference | OpenBB SDK Docs" />

Get latest insider sales

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/sdk_helper.py#L168)]

```python wordwrap
openbb.stocks.ins.lis()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of latest insider trades |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.stocks.ins.lis()
```

---


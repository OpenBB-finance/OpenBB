---
title: blis
description: Get latest insider sales > 100k
keywords:
- stocks
- ins
- blis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ins.blis - Reference | OpenBB SDK Docs" />

Get latest insider sales > 100k

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/sdk_helper.py#L184)]

```python wordwrap
openbb.stocks.ins.blis()
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
openbb.stocks.ins.blis()
```

---


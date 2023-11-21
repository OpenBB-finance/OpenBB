---
title: blcs
description: Get latest CEO/CFO sales > 100k
keywords:
- stocks
- ins
- blcs
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ins.blcs - Reference | OpenBB SDK Docs" />

Get latest CEO/CFO sales > 100k

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/sdk_helper.py#L216)]

```python wordwrap
openbb.stocks.ins.blcs()
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
openbb.stocks.ins.blcs()
```

---


---
title: blcp
description: Get latest CEO/CFO purchases > 25k
keywords:
- stocks
- ins
- blcp
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ins.blcp - Reference | OpenBB SDK Docs" />

Get latest CEO/CFO purchases > 25k

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/sdk_helper.py#L152)]

```python wordwrap
openbb.stocks.ins.blcp()
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
openbb.stocks.ins.blcp()
```

---


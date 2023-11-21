---
title: blip
description: Get latest insider purchases > 25k
keywords:
- stocks
- ins
- blip
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ins.blip - Reference | OpenBB SDK Docs" />

Get latest insider purchases > 25k

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/sdk_helper.py#L120)]

```python wordwrap
openbb.stocks.ins.blip()
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
openbb.stocks.ins.blip()
```

---


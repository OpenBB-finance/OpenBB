---
title: lip
description: Get latest insider purchases
keywords:
- stocks
- ins
- lip
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ins.lip - Reference | OpenBB SDK Docs" />

Get latest insider purchases

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/sdk_helper.py#L104)]

```python wordwrap
openbb.stocks.ins.lip()
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
openbb.stocks.ins.lip()
```

---


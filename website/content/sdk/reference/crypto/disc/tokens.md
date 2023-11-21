---
title: tokens
description: Get chains that support tokens [Source https//dappradar
keywords:
- crypto
- disc
- tokens
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.disc.tokens - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get chains that support tokens [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_model.py#L369)]

```python wordwrap
openbb.crypto.disc.tokens()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Columns: Chains |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing chains that support tokens [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_view.py#L311)]

```python wordwrap
openbb.crypto.disc.tokens_chart(export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
---
title: dapp_categories
description: Get dapp categories [Source https//dappradar
keywords:
- crypto
- disc
- dapp_categories
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.disc.dapp_categories - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get dapp categories [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_model.py#L234)]

```python wordwrap
openbb.crypto.disc.dapp_categories()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Columns: Category |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing dapp categories [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_view.py#L173)]

```python wordwrap
openbb.crypto.disc.dapp_categories_chart(export: str = "", sheet_name: Optional[str] = None)
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
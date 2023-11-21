---
title: defi_chains
description: Get defi chains [Source https//dappradar
keywords:
- crypto
- disc
- defi_chains
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.disc.defi_chains - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get defi chains [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_model.py#L347)]

```python wordwrap
openbb.crypto.disc.defi_chains()
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

Prints table showing defi chains [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_view.py#L286)]

```python wordwrap
openbb.crypto.disc.defi_chains_chart(export: str = "", sheet_name: Optional[str] = None)
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
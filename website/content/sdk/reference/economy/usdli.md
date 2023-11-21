---
title: usdli
description: The USD Liquidity Index is defined as [WALCL - WLRRAL - WDTGAL]
keywords:
- economy
- usdli
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.usdli - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

The USD Liquidity Index is defined as: [WALCL - WLRRAL - WDTGAL]. It is expressed in billions of USD.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/fred_model.py#L391)]

```python wordwrap
openbb.economy.usdli(overlay: str = "", show: bool = False)
```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---



</TabItem>
<TabItem value="view" label="Chart">

Display US Dollar Liquidity

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/fred_view.py#L319)]

```python wordwrap
openbb.economy.usdli_chart(overlay: str = "SP500", show: bool = False, raw: bool = False, export: str = "", sheet_name: Optional[str] = "", external_axes: bool = False)
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
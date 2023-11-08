---
title: positionbook
description: Improve your understanding of the positionbook functionality on the OpenBBTerminal.
  Discover how to request position book data and plot a position book for an instrument
  if Oanda provides one. Detailed source codes and parameter descriptions are provided
  to facilitate its usage.
keywords:
- positionbook
- plotting
- Oanda
- forex
- data frame
- parameters
- currency pair
- matplotlib
- axes
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex.oanda.positionbook - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Request position book data for plotting.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L182)]

```python
openbb.forex.oanda.positionbook(instrument: Optional[str] = None, accountID: str = "REPLACE_ME")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| instrument | Union[str, None] | The loaded currency pair, by default None | None | True |
| accountID | str | Oanda account ID, by default cfg.OANDA_ACCOUNT | REPLACE_ME | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Union[pd.DataFrame, bool] | Position book data or False |
---

</TabItem>
<TabItem value="view" label="Chart">

Plot a position book for an instrument if Oanda provides one.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_view.py#L116)]

```python
openbb.forex.oanda.positionbook_chart(accountID: str, instrument: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda user account ID | None | False |
| instrument | str | The loaded currency pair |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>

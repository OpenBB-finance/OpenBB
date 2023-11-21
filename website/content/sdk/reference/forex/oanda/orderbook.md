---
title: orderbook
description: This documentation page hosts information on 'Orderbook' operations in
  forex trading using the 'Oanda' platform, powered by 'OpenBB'. It includes Python
  source code, various parameters, and return types. Also addressed is plotting an
  'Orderbook' chart with 'matplotlib'.
keywords:
- orderbook
- oanda
- forex
- currency pair
- accountID
- orderbook chart
- matplotlib
- pandas DataFrame
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex.oanda.orderbook - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Request order book data for plotting.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L145)]

```python wordwrap
openbb.forex.oanda.orderbook(instrument: Optional[str] = None, accountID: str = "REPLACE_ME")
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
| Union[pd.DataFrame, bool] | Order book data or False |
---



</TabItem>
<TabItem value="view" label="Chart">

Plot the orderbook for the instrument if Oanda provides one.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_view.py#L73)]

```python wordwrap
openbb.forex.oanda.orderbook_chart(accountID: str, instrument: str = "", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda user account ID | None | False |
| instrument | str | The loaded currency pair |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
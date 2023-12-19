---
title: btc_transac
description: This documentation page provides code and information about retrieving
  and visualizing BTC confirmed transactions using OpenBB. It includes python code
  and detailed parameters' description for the functions.
keywords:
- BTC confirmed transactions
- API
- blockchain.info
- Data Export
- Data Visualization
- crypto.onchain.btc_transac
- crypto.onchain.btc_transac_chart
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.onchain.btc_transac - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns BTC confirmed transactions [Source: https://api.blockchain.info/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/blockchain_model.py#L62)]

```python
openbb.crypto.onchain.btc_transac()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | BTC confirmed transactions |
---

</TabItem>
<TabItem value="view" label="Chart">

Returns BTC confirmed transactions [Source: https://api.blockchain.info/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/blockchain_view.py#L88)]

```python
openbb.crypto.onchain.btc_transac_chart(start_date: str = "2010-01-01", end_date: Optional[str] = None, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | str | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | Optional[str] | Final date, format YYYY-MM-DD | None | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>

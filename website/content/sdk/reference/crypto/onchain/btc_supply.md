---
title: btc_supply
description: This documentation page provides codes and guidelines on how to obtain
  information about the circulating supply of Bitcoin (BTC) through OpenBBTerminal's
  onchain modules. It details the function to use, parameters needed, and the expected
  returns.
keywords:
- Bitcoin circulating supply
- BTC supply
- Blockchain information
- Cryptocurrency
- Onchain
- Data
- API
- Source code
- Function
- Parameters
- Returns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.onchain.btc_supply - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns BTC circulating supply [Source: https://api.blockchain.info/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/blockchain_model.py#L80)]

```python wordwrap
openbb.crypto.onchain.btc_supply()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | BTC circulating supply |
---



</TabItem>
<TabItem value="view" label="Chart">

Returns BTC circulating supply [Source: https://api.blockchain.info/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/blockchain_view.py#L22)]

```python wordwrap
openbb.crypto.onchain.btc_supply_chart(start_date: str = "2010-01-01", end_date: Optional[str] = None, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | str | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | Optional[str] | Final date, format YYYY-MM-DD | None | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
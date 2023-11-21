---
title: platforms
description: This page contains a directory of all smart contract platforms such
  as Ethereum, Solana, Cosmos, Polkadot, and Kusama. The page provides source codes
  and instructs the use of functionalities in two formats model and chart.
keywords:
- smart contract platforms
- Ethereum
- Solana
- Cosmos
- Polkadot
- Kusama
- model view
- chart view
- cryptocurrency
- openbb.crypto.ov.platforms()
- openbb.crypto.ov.platforms_chart()
- CoinPaprika
- dataframe export
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.ov.platforms - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama ... [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_model.py#L376)]

```python wordwrap
openbb.crypto.ov.platforms()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | index, platform_id |
---



</TabItem>
<TabItem value="view" label="Chart">

List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_view.py#L343)]

```python wordwrap
openbb.crypto.ov.platforms_chart(export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
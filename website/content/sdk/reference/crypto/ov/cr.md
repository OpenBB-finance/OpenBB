---
title: cr
description: Documentation for two functions providing cryptocurrency interest rates
  for both borrowing and supplying.You can use the functions to export data or generate
  charts. Several platforms are covered including BlockFi, Ledn, SwissBorg, and Youhodler.
keywords:
- Cryptocurrency
- Crypto Interest Rates
- Crypto Borrowing
- Crypto Supplying
- Interest Rate Platforms
- Crypto Charts
- Crypto Data Export
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.ov.cr - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns crypto {borrow,supply} interest rates for cryptocurrencies across several platforms

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/loanscan_model.py#L267)]

```python
openbb.crypto.ov.cr(rate_type: str = "borrow")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| rate_type | str | Interest rate type: {borrow, supply}. Default: supply | borrow | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | crypto interest rates per platform |
---

</TabItem>
<TabItem value="view" label="Chart">

Displays crypto {borrow,supply} interest rates for cryptocurrencies across several platforms

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/loanscan_view.py#L24)]

```python
openbb.crypto.ov.cr_chart(symbols: str, platforms: str, rate_type: str = "borrow", limit: int = 10, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| rate_type | str | Interest rate type: {borrow, supply}. Default: supply | borrow | True |
| symbols | str | Crypto separated by commas. Default: BTC,ETH,USDT,USDC | None | False |
| platforms | str | Platforms separated by commas. Default: BlockFi,Ledn,SwissBorg,Youhodler | None | False |
| limit | int | Number of records to show | 10 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>

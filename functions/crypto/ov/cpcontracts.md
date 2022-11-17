---
title: cpcontracts
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cpcontracts

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_ov_coinpaprika_model.get_contract_platform

```python title='openbb_terminal/cryptocurrency/overview/coinpaprika_model.py'
def get_contract_platform(platform_id: str, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_model.py#L419)

Description: Gets all contract addresses for given platform [Source: CoinPaprika]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| platform_id | str | Blockchain platform like eth-ethereum | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascend | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | id, type, active |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_ov_coinpaprika_view.display_contracts

```python title='openbb_terminal/cryptocurrency/overview/coinpaprika_view.py'
def display_contracts(symbol: str, sortby: str, ascend: bool, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_view.py#L349)

Description: Gets all contract addresses for given platform. [Source: CoinPaprika]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| platform | str | Blockchain platform like eth-ethereum | None | False |
| limit | int | Number of records to display | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascending | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
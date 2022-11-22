---
title: vaults
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# vaults

<Tabs>
<TabItem value="model" label="Model" default>

Get DeFi Vaults Information. DeFi Vaults are pools of funds with an assigned strategy which main goal is to

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/coindix_model.py#L107)]

```python
openbb.crypto.defi.vaults(chain: Optional[str] = None, protocol: Optional[str] = None, kind: Optional[str] = None, ascend: bool = True, sortby: str = "apy")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| chain | str | Blockchain - one from list [<br/>'ethereum', 'polygon', 'avalanche', 'bsc', 'terra', 'fantom',<br/>'moonriver', 'celo', 'heco', 'okex', 'cronos', 'arbitrum', 'eth',<br/>'harmony', 'fuse', 'defichain', 'solana', 'optimism'<br/>] | None | True |
| protocol | str | DeFi protocol - one from list: [<br/>'aave', 'acryptos', 'alpaca', 'anchor', 'autofarm', 'balancer', 'bancor',<br/>'beefy', 'belt', 'compound', 'convex', 'cream', 'curve', 'defichain', 'geist',<br/>'lido', 'liquity', 'mirror', 'pancakeswap', 'raydium', 'sushi', 'tarot', 'traderjoe',<br/>'tulip', 'ubeswap', 'uniswap', 'venus', 'yearn'<br/>] | None | True |
| kind | str | Kind/type of vault - one from list: ['lp','single','noimploss','stable'] | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Top 100 DeFi Vaults for given chain/protocol sorted by APY. |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing Top DeFi Vaults - pools of funds with an assigned strategy which main goal is to

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/coindix_view.py#L19)]

```python
openbb.crypto.defi.vaults_chart(chain: Optional[str] = None, protocol: Optional[str] = None, kind: Optional[str] = None, limit: int = 10, sortby: str = "apy", ascend: bool = True, link: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| chain | str | Blockchain - one from list [<br/>'ethereum', 'polygon', 'avalanche', 'bsc', 'terra', 'fantom',<br/>'moonriver', 'celo', 'heco', 'okex', 'cronos', 'arbitrum', 'eth',<br/>'harmony', 'fuse', 'defichain', 'solana', 'optimism'<br/>] | None | True |
| protocol | str | DeFi protocol - one from list: [<br/>'aave', 'acryptos', 'alpaca', 'anchor', 'autofarm', 'balancer', 'bancor',<br/>'beefy', 'belt', 'compound', 'convex', 'cream', 'curve', 'defichain', 'geist',<br/>'lido', 'liquity', 'mirror', 'pancakeswap', 'raydium', 'sushi', 'tarot', 'traderjoe',<br/>'tulip', 'ubeswap', 'uniswap', 'venus', 'yearn'<br/>] | None | True |
| kind | str | Kind/type of vault - one from list: ['lp','single','noimploss','stable'] | None | True |
| limit | int | Number of records to display | 10 | True |
| sortby | str | Key by which to sort data | apy | True |
| ascend | bool | Flag to sort data descending | True | True |
| link | bool | Flag to show links | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
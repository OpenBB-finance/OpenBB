---
title: btcsingleblock
description: Returns BTC block data in json format
keywords:
- crypto
- onchain
- btcsingleblock
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.onchain.btcsingleblock - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns BTC block data in json format. [Source: https://blockchain.info/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/blockchain_model.py#L118)]

```python wordwrap
openbb.crypto.onchain.btcsingleblock(blockhash: str)
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | BTC single block |
---



</TabItem>
<TabItem value="view" label="Chart">

Returns BTC block data. [Source: https://api.blockchain.info/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/blockchain_view.py#L126)]

```python wordwrap
openbb.crypto.onchain.btcsingleblock_chart(blockhash: str, export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| blockhash | str | Hash of the block you are looking for. | None | False |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
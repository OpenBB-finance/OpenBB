---
title: nft_mktp_chains
description: Get nft marketplaces chains [Source https//dappradar
keywords:
- crypto
- disc
- nft_mktp_chains
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.disc.nft_mktp_chains - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get nft marketplaces chains [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_model.py#L142)]

```python wordwrap
openbb.crypto.disc.nft_mktp_chains()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Columns: Chain |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing nft marketplaces chains [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_view.py#L85)]

```python wordwrap
openbb.crypto.disc.nft_mktp_chains_chart(export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| sheet_name | str | Name of the sheet in excel or csv file | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
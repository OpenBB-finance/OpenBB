---
title: top
description: Documentation for the OpenBB project's top 50 crypto tokens function.
  This is implemented in Python and uses Docusaurus to organize and render the documentation.
  It covers the parameters required and the expected result, including the sort order
  and the type of data rendered.
keywords:
- Docusaurus
- Metadata
- Top 50 Tokens
- Cryptocurrency
- ERC20
- Ethplorer
- Cryptocurrency Rank
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.onchain.top - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get top 50 tokens. [Source: Ethplorer]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/ethplorer_model.py#L268)]

```python
openbb.crypto.onchain.top(sortby: str = "rank", ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Key to sort by. | rank | True |
| ascend | str | Sort in descending order. | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with list of top 50 tokens. |
---

</TabItem>
<TabItem value="view" label="Chart">

Display top ERC20 tokens [Source: Ethplorer]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/ethplorer_view.py#L70)]

```python
openbb.crypto.onchain.top_chart(limit: int = 15, sortby: str = "rank", ascend: bool = True, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Limit of transactions. Maximum 100 | 15 | True |
| sortby | str | Key to sort by. | rank | True |
| ascend | str | Sort in descending order. | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>

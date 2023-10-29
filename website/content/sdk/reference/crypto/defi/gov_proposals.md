---
title: gov_proposals
description: Docusaurus page about Terra blockchain governance proposals, detailing
  parameters and functionalities such as sorting, ascending/descending and exporting
  data. Includes links to original source and GitHub source.
keywords:
- Terra Blockchain
- Governance Proposals
- Sorting Data
- Ascending
- Descending
- Exporting Data
- Source Code
- Docusaurus Page SEO
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.defi.gov_proposals - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terramoney_fcd_model.py#L197)]

```python
openbb.crypto.defi.gov_proposals(status: str = "", sortby: str = "id", ascend: bool = True, limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| status | str | status of proposal, one from list: ['Voting','Deposit','Passed','Rejected'] |  | True |
| sortby | str | Key by which to sort data | id | True |
| ascend | bool | Flag to sort data ascending | True | True |
| limit | int | Number of records to display | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Terra blockchain governance proposals list |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terramoney_fcd_view.py#L108)]

```python
openbb.crypto.defi.gov_proposals_chart(limit: int = 10, status: str = "all", sortby: str = "id", ascend: bool = True, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 10 | True |
| status | str | status of proposal, one from list: ['Voting','Deposit','Passed','Rejected'] | all | True |
| sortby | str | Key by which to sort data | id | True |
| ascend | bool | Flag to sort data ascend | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>

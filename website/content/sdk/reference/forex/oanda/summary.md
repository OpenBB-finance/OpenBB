---
title: summary
description: This is a comprehensive documentation on the functionality of creating
  an Oanda account summary using OpenBB-Finance. Covers Python source codes, parameters
  and returns on model and chart tabs for summary creation.
keywords:
- Oanda account summary
- Source Code
- OpenBB finance
- forex
- oanda_model.py
- oanda_view.py
- account ID
- TabItem
- Tabs
- Union
- summary chart
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex.oanda.summary - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Request Oanda account summary.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L74)]

```python
openbb.forex.oanda.summary(accountID: str = "REPLACE_ME")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda account ID, by default cfg.OANDA_ACCOUNT | REPLACE_ME | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Union[pd.DataFrame, bool] | Account summary data or False |
---

</TabItem>
<TabItem value="view" label="Chart">

Print Oanda account summary.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_view.py#L62)]

```python
openbb.forex.oanda.summary_chart(accountID: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| accountID | str | Oanda user account ID | None | False |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>

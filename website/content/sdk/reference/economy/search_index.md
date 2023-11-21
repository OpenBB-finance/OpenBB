---
title: search_index
description: This Docusaurus page provides information about how to use the 'search_index'
  function from the OpenBB finance package. It explains the parameters and returns
  of this function, which helps to search indices by keyword in the finance database.
  Source code is also provided.
keywords:
- search_index
- OpenBB finance package
- finance database
- keyword search
- parameters
- returns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.search_index - Reference | OpenBB SDK Docs" />

Search indices by keyword. [Source: FinanceDatabase]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/yfinance_model.py#L733)]

```python wordwrap
openbb.economy.search_index(keyword: list)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| keyword | list | The keyword you wish to search for. This can include spaces. | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Dataframe | Dataframe with the available options. |
---


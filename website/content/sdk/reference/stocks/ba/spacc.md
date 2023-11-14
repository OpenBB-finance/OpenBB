---
title: spacc
description: Detailed documentation of the function openbb.stocks.ba.spacc, providing
  insights into top trending SPACs on Reddit. The page includes the source code, parameters,
  and returns for implementing the function.
keywords:
- SPACs
- Reddit
- Source Code
- openbb.stocks.ba.spacc
- Parameters
- Returns
- dictionary
- Number of mentions
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.spacc - Reference | OpenBB SDK Docs" />

Get top tickers from r/SPACs [Source: reddit].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/reddit_model.py#L317)]

```python
openbb.stocks.ba.spacc(limit: int = 10, popular: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of posts to look at | 10 | True |
| popular | bool | Search by hot instead of new | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, dict] | Dataframe of reddit submission,<br/>Dictionary of tickers and number of mentions. |
---

---
title: mgmt
description: This page provides a guide on getting company managers' details from
  Business Insider using the OpenBB library. Code snippet in Python is provided.
keywords:
- company managers
- Business Insider
- OpenBB library
- Python code
- Stock ticker symbol
- Dataframe of managers
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.mgmt - Reference | OpenBB SDK Docs" />

Get company managers from Business Insider

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/business_insider_model.py#L19)]

```python
openbb.stocks.fa.mgmt(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of managers |
---

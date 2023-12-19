---
title: fwd
description: This documentation page provides the syntax and details for extracting
  forward rates from fxempire using the OpenBB.finance OpenBBTerminal, including the
  parameters required and the return type. The page is of significant utility to users
  seeking to navigate the forex section of the OpenBBTerminal.
keywords:
- fwd function
- fxempire
- Forward rates
- forex
- OpenBB.finance
- currency conversion
- USD
- EUR
- parameters
- returns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex.fwd - Reference | OpenBB SDK Docs" />

Gets forward rates from fxempire

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/fxempire_model.py#L14)]

```python
openbb.forex.fwd(to_symbol: str = "USD", from_symbol: str = "EUR")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| to_symbol | str | To currency | USD | True |
| from_symbol | str | From currency | EUR | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing forward rates |
---

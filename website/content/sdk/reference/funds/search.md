---
title: search
description: Search mstarpy for matching funds
keywords:
- funds
- search
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="funds.search - Reference | OpenBB SDK Docs" />

Search mstarpy for matching funds

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/mstarpy_model.py#L212)]

```python wordwrap
openbb.funds.search(term: str = "", country: str = "", limit: Any = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| term | str | String that will be searched for.  Can be name or isin |  | True |
| field | list | list of field who will be displayed | None | True |
| country | str | country where the funds is hosted |  | True |
| limit | int | length of results to display | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing matches |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.funds.search("Vanguard", "US")
```

---


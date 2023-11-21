---
title: estr
description: Obtain data for Euro Short-Term Rate (ESTR)
keywords:
- fixedincome
- estr
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.estr - Reference | OpenBB SDK Docs" />

Obtain data for Euro Short-Term Rate (ESTR)

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L430)]

```python wordwrap
openbb.fixedincome.estr(parameter: str = "volume_weighted_trimmed_mean_rate", start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| parameter | str | The parameter to get data for. | volume_weighted_trimmed_mean_rate | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |


---

## Returns

This function does not return anything

---


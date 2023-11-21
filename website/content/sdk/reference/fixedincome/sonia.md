---
title: sonia
description: Obtain data for Sterling Overnight Index Average (SONIA)
keywords:
- fixedincome
- sonia
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.sonia - Reference | OpenBB SDK Docs" />

Obtain data for Sterling Overnight Index Average (SONIA)

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L487)]

```python wordwrap
openbb.fixedincome.sonia(parameter: str = "rate", start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| parameter | str | The parameter to get data for. | rate | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |


---

## Returns

This function does not return anything

---


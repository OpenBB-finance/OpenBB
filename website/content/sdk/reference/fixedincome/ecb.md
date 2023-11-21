---
title: ecb
description: Obtain data for ECB interest rates
keywords:
- fixedincome
- ecb
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.ecb - Reference | OpenBB SDK Docs" />

Obtain data for ECB interest rates.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L688)]

```python wordwrap
openbb.fixedincome.ecb(interest_type: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| interest_type | Optional[str] | The ability to decide what interest rate to plot. Choose from:<br/>    "deposit"<br/>    "lending"<br/>    "refinancing" | None | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |


---

## Returns

This function does not return anything

---


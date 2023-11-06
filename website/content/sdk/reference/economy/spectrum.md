---
title: spectrum
description: Learn how to use the OpenBB economy spectrum function to display the
  finviz spectrum in your system viewer. Understand parameters like group and export,
  and learn how to customize them for your needs.
keywords:
- spectrum
- finviz
- openbb.economy.spectrum
- group
- export
- get_groups()
- sector
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.spectrum - Reference | OpenBB SDK Docs" />

Display finviz spectrum in system viewer [Source: Finviz]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/finviz_view.py#L111)]

```python
openbb.economy.spectrum(group: str = "sector", export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| group | str | Group by category. Available groups can be accessed through get_groups(). | sector | True |
| export | str | Format to export data |  | True |


---

## Returns

This function does not return anything

---

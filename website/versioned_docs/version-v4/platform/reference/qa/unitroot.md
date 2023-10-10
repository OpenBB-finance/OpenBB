---
title: unitroot
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# unitroot

Get Unit Root Test.

    Augmented Dickey-Fuller test for unit root.
    Kwiatkowski-Phillips-Schmidt-Shin test for unit root.

    Parameters
    ----------
    data : List[Data]
        Time series data.
    target : str
        Target column name.
    fuller_reg : Literal["c", "ct", "ctt", "nc", "c"]
        Regression type for ADF test.
    kpss_reg : Literal["c", "ct"]
        Regression type for KPSS test.

    Returns
    -------
    OBBject[UnitRootModel]
        Unit root tests summary.

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---


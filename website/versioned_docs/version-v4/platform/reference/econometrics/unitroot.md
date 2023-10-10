---
title: unitroot
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# unitroot

Perform Augmented Dickey-Fuller unit root test.

    Parameters
    ----------
    data: List[Data]
        Input dataset.
    column: str
        Data columns to check unit root
    regression: str
        Regression type to use in the test.  Either "c" for constant only, "ct" for constant and trend, or "ctt" for
        constant, trend, and trend-squared.
    Returns
    -------
    OBBject[Data]
        OBBject with the results being the score from the test.

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---


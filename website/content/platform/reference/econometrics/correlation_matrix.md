---
title: "correlation_matrix"
description: "Learn how to get the correlation matrix of an input dataset using Python.  Find information on the parameters and return value of the function."
keywords:
- correlation matrix
- input dataset
- Python
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics/correlation_matrix - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the correlation matrix of an input dataset.

 The correlation matrix provides a view of how different variables in your dataset relate to one another.
 By quantifying the degree to which variables move in relation to each other, this matrix can help identify patterns,
 trends, and potential areas for deeper analysis. The correlation score ranges from -1 to 1, with -1 indicating a
 perfect negative correlation, 0 indicating no correlation, and 1 indicating a perfect positive correlation.


Examples
--------

```python
from openbb import obb
# Get the correlation matrix of a dataset.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()
obb.econometrics.correlation_matrix(data=stock_data)
obb.econometrics.correlation_matrix(data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Input dataset. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        Correlation matrix.
```


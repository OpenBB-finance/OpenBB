---
title: "summary"
description: "Learn how to get summary statistics on time series data using Python.  This documentation page provides information on the parameters and return value  of the function."
keywords:
- summary statistics
- get summary statistics
- summary table
- python
- time series data
- target column
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative/summary - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get Summary Statistics.

 The summary that offers a snapshot of its central tendencies, variability, and distribution.
 This command calculates essential statistics, including mean, standard deviation, variance,
 and specific percentiles, to provide a detailed profile of your target column. B
 y examining these metrics, you gain insights into the data's overall behavior, helping to identify patterns,
 outliers, or anomalies. The summary table is an invaluable tool for initial data exploration,
 ensuring you have a solid foundation for further analysis or reporting.


Examples
--------

```python
from openbb import obb
# Get Summary Statistics.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()
obb.quantitative.summary(data=stock_data, target='close')
obb.quantitative.summary(target='close', data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Time series data. |  | False |
| target | str | Target column name. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : SummaryModel
        Summary table.
```


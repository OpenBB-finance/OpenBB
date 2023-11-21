---
title: cointegration
description: Learn how to use the two-step Engle-Granger test to show co-integration
  between two time series in Python. Explore the parameters, input dataset, data columns,
  and the OBBject returned with the test results.
keywords:
- co-integration
- Engle-Granger test
- time series
- data
- columns
- cointegration
- maxlag
- Python
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /cointegration - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Show co-integration between two timeseries using the two step Engle-Granger test.

```python wordwrap
obb.econometrics.cointegration(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], columns: List[str], maxlag: PositiveInt = None)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Input dataset. | None | False |
| columns | List[str] | Data columns to check cointegration | None | False |
| maxlag | PositiveInt | Number of lags to use in the test. | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject with the results being the score from the test.
```

---


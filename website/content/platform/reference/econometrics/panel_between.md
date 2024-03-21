---
title: "panel_between"
description: "Perform a Between estimator regression on panel data. This page provides  details on the parameters required and the returned OBBject with the fit model."
keywords:
- Between estimator
- regression
- panel data
- perform
- parameters
- data
- y_column
- x_columns
- exogenous variables
- returns
- fit model
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics/panel_between - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform a Between estimator regression on panel data.

 The Between estimator for regression analysis on panel data is focusing on the differences between entities
 (such as individuals, companies, or countries) over time. By aggregating the data for each entity and analyzing the
 average outcomes, this method provides insights into the overall impact of explanatory variables (x_columns) on
 the dependent variable (y_column) across all entities.


Examples
--------

```python
from openbb import obb
obb.econometrics.panel_between(y_column='portfolio_value', x_columns=['risk_free_rate'], data=[{'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_1', 'time': 0, 'portfolio_value': 100000.0, 'risk_free_rate': 0.02}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_1', 'time': 1, 'portfolio_value': 150000.0, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_2', 'time': 0, 'portfolio_value': 150000.0, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_2', 'time': 1, 'portfolio_value': 133333.33, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_3', 'time': 0, 'portfolio_value': 133333.33, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_3', 'time': 1, 'portfolio_value': 125000.0, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_4', 'time': 0, 'portfolio_value': 125000.0, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_4', 'time': 1, 'portfolio_value': 120000.0, 'risk_free_rate': 0.02}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_5', 'time': 0, 'portfolio_value': 120000.0, 'risk_free_rate': 0.02}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_5', 'time': 1, 'portfolio_value': 116666.67, 'risk_free_rate': 0.02}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Input dataset. |  | False |
| y_column | str | Target column. |  | False |
| x_columns | List[str] | List of columns to use as exogenous variables. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : Dict
        OBBject with the fit model returned
```


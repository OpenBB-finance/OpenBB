---
title: "panel_fmac"
description: "Learn how to use the Fama-MacBeth estimator for panel data analysis in  Python. Understand the parameters required and how to specify the input dataset  and target column. Explore how this function can help you analyze panel data by  incorporating exogenous variables."
keywords:
- Fama-MacBeth estimator
- panel data analysis
- Python function
- parameters
- exogenous variables
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics/panel_fmac - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Fama-MacBeth estimator for panel data.

 The Fama-MacBeth estimator, a two-step procedure renowned for its application in finance to estimate the risk
 premiums and evaluate the capital asset pricing model. By first estimating cross-sectional regressions for each
 time period and then averaging the regression coefficients over time, this method provides insights into the
 relationship between the dependent variable (y_column) and explanatory variables (x_columns) across different
 entities (such as individuals, companies, or countries).


Examples
--------

```python
from openbb import obb
obb.econometrics.panel_fmac(y_column='portfolio_value', x_columns=['risk_free_rate'], data=[{'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_1', 'time': 0, 'portfolio_value': 100000.0, 'risk_free_rate': 0.02}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_1', 'time': 1, 'portfolio_value': 150000.0, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_2', 'time': 0, 'portfolio_value': 150000.0, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_2', 'time': 1, 'portfolio_value': 133333.33, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_3', 'time': 0, 'portfolio_value': 133333.33, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_3', 'time': 1, 'portfolio_value': 125000.0, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_4', 'time': 0, 'portfolio_value': 125000.0, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_4', 'time': 1, 'portfolio_value': 120000.0, 'risk_free_rate': 0.02}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_5', 'time': 0, 'portfolio_value': 120000.0, 'risk_free_rate': 0.02}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_5', 'time': 1, 'portfolio_value': 116666.67, 'risk_free_rate': 0.02}])
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


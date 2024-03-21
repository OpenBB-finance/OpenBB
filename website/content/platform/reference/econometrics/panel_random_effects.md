---
title: "panel_random_effects"
description: "Learn how to perform One-way Random Effects model for panel data using  a Python function. This function takes an input dataset, target column, and exogenous  variables as parameters and returns the fit model."
keywords:
- One-way Random Effects model
- panel data
- perform
- Python function
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics/panel_random_effects - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform One-way Random Effects model for panel data.

 One-way Random Effects model to panel data is offering a nuanced approach to analyzing data that spans across both
 time and entities (such as individuals, companies, countries, etc.). By acknowledging and modeling the random
 variation that exists within these entities, this method provides insights into the general patterns that
 emerge across the dataset.


Examples
--------

```python
from openbb import obb
obb.econometrics.panel_random_effects(y_column='portfolio_value', x_columns=['risk_free_rate'], data=[{'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_1', 'time': 0, 'portfolio_value': 100000.0, 'risk_free_rate': 0.02}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_1', 'time': 1, 'portfolio_value': 150000.0, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_2', 'time': 0, 'portfolio_value': 150000.0, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_2', 'time': 1, 'portfolio_value': 133333.33, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_3', 'time': 0, 'portfolio_value': 133333.33, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_3', 'time': 1, 'portfolio_value': 125000.0, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_4', 'time': 0, 'portfolio_value': 125000.0, 'risk_free_rate': 0.03}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_4', 'time': 1, 'portfolio_value': 120000.0, 'risk_free_rate': 0.02}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_5', 'time': 0, 'portfolio_value': 120000.0, 'risk_free_rate': 0.02}, {'is_multiindex': True, 'multiindex_names': "['asset_manager', 'time']", 'asset_manager': 'asset_manager_5', 'time': 1, 'portfolio_value': 116666.67, 'risk_free_rate': 0.02}])
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


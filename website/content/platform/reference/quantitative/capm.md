---
title: "capm"
description: "Learn about the Capital Asset Pricing Model (CAPM), a widely-used finance  theory for determining an investment's expected return based on its risk. Understand  how CAPM can be used as an investment strategy to evaluate and select securities."
keywords:
- capital asset pricing model
- CAPM
- finance
- investment strategy
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative/capm - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get Capital Asset Pricing Model (CAPM).

 CAPM offers a streamlined way to assess the expected return on an investment while accounting for its risk relative
 to the market. It's a cornerstone of modern financial theory that helps investors understand the trade-off between
 risk and return, guiding more informed investment choices.


Examples
--------

```python
from openbb import obb
# Get Capital Asset Pricing Model (CAPM).
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()
obb.quantitative.capm(data=stock_data, target='close')
obb.quantitative.capm(target='close', data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}, {'date': '2023-01-07', 'open': 128.33, 'high': 140.0, 'low': 116.67, 'close': 134.17, 'volume': 11666.67}, {'date': '2023-01-08', 'open': 125.71, 'high': 137.14, 'low': 114.29, 'close': 131.43, 'volume': 11428.57}, {'date': '2023-01-09', 'open': 123.75, 'high': 135.0, 'low': 112.5, 'close': 129.38, 'volume': 11250.0}, {'date': '2023-01-10', 'open': 122.22, 'high': 133.33, 'low': 111.11, 'close': 127.78, 'volume': 11111.11}, {'date': '2023-01-11', 'open': 121.0, 'high': 132.0, 'low': 110.0, 'close': 126.5, 'volume': 11000.0}, {'date': '2023-01-12', 'open': 120.0, 'high': 130.91, 'low': 109.09, 'close': 125.45, 'volume': 10909.09}, {'date': '2023-01-13', 'open': 119.17, 'high': 130.0, 'low': 108.33, 'close': 124.58, 'volume': 10833.33}, {'date': '2023-01-14', 'open': 118.46, 'high': 129.23, 'low': 107.69, 'close': 123.85, 'volume': 10769.23}, {'date': '2023-01-15', 'open': 117.86, 'high': 128.57, 'low': 107.14, 'close': 123.21, 'volume': 10714.29}, {'date': '2023-01-16', 'open': 117.33, 'high': 128.0, 'low': 106.67, 'close': 122.67, 'volume': 10666.67}, {'date': '2023-01-17', 'open': 116.88, 'high': 127.5, 'low': 106.25, 'close': 122.19, 'volume': 10625.0}, {'date': '2023-01-18', 'open': 116.47, 'high': 127.06, 'low': 105.88, 'close': 121.76, 'volume': 10588.24}, {'date': '2023-01-19', 'open': 116.11, 'high': 126.67, 'low': 105.56, 'close': 121.39, 'volume': 10555.56}, {'date': '2023-01-20', 'open': 115.79, 'high': 126.32, 'low': 105.26, 'close': 121.05, 'volume': 10526.32}, {'date': '2023-01-21', 'open': 115.5, 'high': 126.0, 'low': 105.0, 'close': 120.75, 'volume': 10500.0}, {'date': '2023-01-22', 'open': 115.24, 'high': 125.71, 'low': 104.76, 'close': 120.48, 'volume': 10476.19}, {'date': '2023-01-23', 'open': 115.0, 'high': 125.45, 'low': 104.55, 'close': 120.23, 'volume': 10454.55}, {'date': '2023-01-24', 'open': 114.78, 'high': 125.22, 'low': 104.35, 'close': 120.0, 'volume': 10434.78}, {'date': '2023-01-25', 'open': 114.58, 'high': 125.0, 'low': 104.17, 'close': 119.79, 'volume': 10416.67}, {'date': '2023-01-26', 'open': 114.4, 'high': 124.8, 'low': 104.0, 'close': 119.6, 'volume': 10400.0}, {'date': '2023-01-27', 'open': 114.23, 'high': 124.62, 'low': 103.85, 'close': 119.42, 'volume': 10384.62}, {'date': '2023-01-28', 'open': 114.07, 'high': 124.44, 'low': 103.7, 'close': 119.26, 'volume': 10370.37}, {'date': '2023-01-29', 'open': 113.93, 'high': 124.29, 'low': 103.57, 'close': 119.11, 'volume': 10357.14}, {'date': '2023-01-30', 'open': 113.79, 'high': 124.14, 'low': 103.45, 'close': 118.97, 'volume': 10344.83}, {'date': '2023-01-31', 'open': 113.67, 'high': 124.0, 'low': 103.33, 'close': 118.83, 'volume': 10333.33}, {'date': '2023-02-01', 'open': 113.55, 'high': 123.87, 'low': 103.23, 'close': 118.71, 'volume': 10322.58}])
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
    results : CAPMModel
        CAPM model summary.
```


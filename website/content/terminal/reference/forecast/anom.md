---
title: anom
description: Perform a Quantile Anomaly detection on a given dataset https//unit8co
keywords:
- forecast
- anom
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast /anom - Reference | OpenBB Terminal Docs" />

Perform a Quantile Anomaly detection on a given dataset: https://unit8co.github.io/darts/generated_api/darts.ad.detectors.quantile_detector.html

### Usage

```python wordwrap
anom [-d {AAPL}] [-c TARGET_COLUMN] [-t TRAIN_SPLIT] [--end S_END_DATE] [--start S_START_DATE] [--forecast-only]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| target_dataset | -d  --dataset | The name of the dataset you want to select | None | True | AAPL |
| target_column | -c  --target-column | The name of the specific column you want to use | close | True | None |
| train_split | -t  --train-split | Start point for rolling training and forecast window. 0.0-1.0 | 0.85 | True | None |
| s_end_date | --end | The end date (format YYYY-MM-DD) to select for testing | None | True | None |
| s_start_date | --start | The start date (format YYYY-MM-DD) to select for testing | None | True | None |
| forecast_only | --forecast-only | Do not plot the historical data without forecasts. | False | True | None |

---

---
title: timegpt
description: TODO Update me
keywords:
- forecast
- timegpt
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast /timegpt - Reference | OpenBB Terminal Docs" />

TODO: Update me

### Usage

```python wordwrap
timegpt [--horizon HORIZON] [--freq {H,D,W,M,MS,B}] [--finetune FINETUNE] [--ci CONFIDENCE] [--cleanex] [--timecol TIMECOL] [--targetcol TARGETCOL] [--sheet-name SHEET_NAME] [--datefeatures DATE_FEATURES] [-d {AAPL}] [-c TARGET_COLUMN] [--end S_END_DATE] [--start S_START_DATE] [--residuals]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| horizon | --horizon | Forecasting horizon | 12 | True | None |
| freq | --freq | Frequency of the data. | None | True | H, D, W, M, MS, B |
| finetune | --finetune | Number of steps used to finetune TimeGPT in the new data. | 0 | True | None |
| confidence | --ci | Number of steps used to finetune TimeGPT in the new data. | 80, 90 | True | None |
| cleanex | --cleanex | Clean exogenous signal before making forecasts using TimeGPT. | True | True | None |
| timecol | --timecol | Dataframe column that represents datetime | ds | True | None |
| targetcol | --targetcol | Dataframe column that represents the target to forecast for | y | True | None |
| sheet_name | --sheet-name | The name of the sheet to export to when type is XLSX. |  | True | None |
| date_features | --datefeatures | Specifies which date attributes have highest weight according to model. |  | True | None |
| target_dataset | -d  --dataset | The name of the dataset you want to select | None | True | AAPL |
| target_column | -c  --target-column | The name of the specific column you want to use | close | True | None |
| s_end_date | --end | The end date (format YYYY-MM-DD) to select for testing | None | True | None |
| s_start_date | --start | The start date (format YYYY-MM-DD) to select for testing | None | True | None |
| residuals | --residuals | Show the residuals for the model. | False | True | None |

---

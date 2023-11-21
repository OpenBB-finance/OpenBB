---
title: vif
description: Calculates VIF (variance inflation factor), which tests collinearity
keywords:
- econometrics
- vif
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /vif - Reference | OpenBB Terminal Docs" />

Calculates VIF (variance inflation factor), which tests collinearity. It quantifies the severity of multicollinearity in an ordinary least squares regression analysis. The square root of the variance inflation factor indicates how much larger the standard error increases compared to if that variable had 0 correlation to other predictor variables in the model. It is defined as: $ VIF_i = 1 / (1 - R_i^2) $ where $ R_i $ is the coefficient of determination of the regression equation with the column i being the result from the i:th series being the exogenous variable. A VIF over 5 indicates a high collinearity and correlation. Values over 10 indicates causes problems, while a value of 1 indicates no correlation. Thus VIF values between 1 and 5 are most commonly considered acceptable. In order to improve the results one can often remove a column with high VIF. For further information see: https://en.wikipedia.org/wiki/Variance_inflation_factor

### Usage

```python wordwrap
vif [-d DATA]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| data | -d  --data | The datasets and columns we want to add dataset,dataset2.column,dataset2.column2 | None | True | None |

---

---
title: dcf
description: OpenBB Terminal Function
---

# dcf

A discounted cash flow statement looks to analyze the value of a company. To do this we need to predict the future cash flows and then determine how much those cash flows are worth to us today. We predict the future expected cash flows by predicting what the financial statements will look like in the future, and then using this to determine the cash the company will have in the future. This cash is paid to share holders. We use linear regression to predict the future financial statements. Once we have our predicted financial statements we need to determine how much the cash flows are worth today. This is done with a discount factor. Our DCF allows users to choose between Fama French and CAPM for the factor. This allows us to calculate the present value of the future cash flows. The present value of all of these cash payments is the companies' value. Dividing this value by the number of shares outstanding allows us to calculate the value of each share in a company.

### Usage

```python
dcf [-a] [--no-ratios] [--no-filter] [-p PREDICTION] [-s SIMILAR] [-g]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| audit | Generates a tie-out for financial statement information pulled from online. | False | True | None |
| ratios | Removes ratios from DCF. | True | True | None |
| ratios | Allow similar companies of any market cap to be shown. | False | True | None |
| prediction | Number of years to predict before using terminal value. | 10 | True | None |
| similar | Number of similar companies to generate ratios for. | 6 | True | None |
| growth | Whether to replace a linear regression estimate with a growth estimate. | False | True | None |

![dcf financials](https://user-images.githubusercontent.com/46355364/154241001-42be82e5-f001-4fd1-bcf4-cd55c7cef358.png)

![dcf free cash flows](https://user-images.githubusercontent.com/46355364/154241130-f52c580e-710d-4cac-a8f3-f9bfece7865a.png)

![dcf explanations](https://user-images.githubusercontent.com/46355364/154241408-5476f0ea-4789-4691-a063-6b43c382fce6.png)

![dcf ratios](https://user-images.githubusercontent.com/46355364/154241575-f931c05a-c765-4abd-9cc1-0a0795aeaec3.png)

---

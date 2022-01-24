```text
usage: dcf [-a] [--no-ratios] [--no-filter] [-p NUM] [-s NUM] [-h]
```

A discounted cash flow statement looks to analyze the value of a company. To do this we need to predict the future cash flows and then determine how much those cash flows are worth to us today.
                
We predict the future expected cash flows by prediciting what the financial statements will look like in the future, and then using this to determine the cash the company will have in the future. This cash is paid to share holders. We us linear regression to predict the future financial statements.
                
Once we have our predicted financial statements we need to determine how much the cash flows are worth today. This is done with a discount factor. Our DCF allows users to choose between Fama French and CAPM for the factor. This allows us to calculate the present value of the future cash flows.

The present value of all of these cash payments is the companies' value. Dividing this value by the number of shares outstanding allows us to calculate the value of each share in a company. Source: https://stockanalysis.com/stocks/

```
optional arguments:
  -a, --audit  Generates a tie-out for financial statement information pulled from online. (default: False)
  --no-ratios  Disables generation of ratio for company and sister companies. (default: False)
  --no-filter  Disables filtering of similar companies based on market cap (default: False)
  -p, --prediction
               The number of years to create financial statements for. (default: 10)
  -s, --sisters
               The number of sister companies to generate ratios for. (default: 3)
  -h, --help   show this help message (default: False)
```
<img size="1400" alt="Feature Sceenshot - dcf" src="https://user-images.githubusercontent.com/85772166/141364660-48ac7da9-129a-452f-baf7-8ced1c2b6031.png">

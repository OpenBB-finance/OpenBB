```text
usage: dcf [-a] [--no-ratios] [--no-filter] [-p NUM] [-s NUM] [-h]
```

Generates a completed discounted cash flow statement as an excel spreadsheet export. The statement uses machine learning to predict future financial statements and share price based on the predicted financials. Source: https://stockanalysis.com/stocks/

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

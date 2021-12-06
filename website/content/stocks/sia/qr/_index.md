```text
usage: qr [-l LIMIT] [-r] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```
https://www.investopedia.com/terms/q/quickratio.asp

The quick ratio is an indicator of a company’s short-term liquidity position and measures a company’s ability to meet its short-term obligations with its most liquid assets.

Since it indicates the company’s ability to instantly use its near-cash assets (assets that can be converted quickly to cash) to pay down its current liabilities, it is also called the acid test ratio. An "acid test" is a slang term for a quick test designed to produce instant results.

Formula for the Quick Ratio

QR = (CE+MS+AR)/CL

Or

QR = (CA-I-PE)/CL

where:
```
QR=Quick ratio
CE=Cash & equivalents
MS=Marketable securities
AR=Accounts receivable
CL=Current Liabilities
CA=Current Assets
I=Inventory
PE=Prepaid expenses
```

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Limit number of companies to display (default: 10)
  -r, --raw             Output all raw data (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

<img size="1400" alt="Feature Screenshot - qr" src="https://user-images.githubusercontent.com/85772166/144781469-c720af9f-1999-4fd3-92bc-14a8acf06d73.png">

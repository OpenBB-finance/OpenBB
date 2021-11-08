```
usage: dpotc [--export {csv,json,xlsx}] [-h]
```

Dark Pool traffic is considered to be all orders executed off-exchange and does not fall under the direct oversight of the SEC, ceding disciplinary actions to the discretion of an industry self-regulating organization, FINRA. The ability to circumvent reporting obligations to the SEC is a major motivating factor in the use of Dark Pools. Discount Brokers typically execute orders through internalizers which are routed through OTC channels, avoiding execution on a public exchange entirely. 

While much of the OTC volume here can be classified as retail purchases through discount brokers, it is important to recognize that OTC transactions frequently happen in the form of block trades and exotic options/derivatives products, and many companies listed on the NASDAQ/NYSE also have dual listings on the OTCX market. 

Alternative Trading Systems (ATS) are off-exchange venues operated by firms with proprietary trading desks. This data is reported weekly and includes individual tickers, the weekly share volume, and the weekly number of total trades. The major advantage a broker/dealer/HF/HFT has over an individual investor is the direct access to live data feeds from the unlit order books held off-exchange. 

The data released to the public as "transparency" is strategically delayed and does not offer direct accountability for the positions held by individual firms. The many loopholes that exist in reporting obligations create an environment favourable to malicious actors and predatory short sellers. The quality of reported data for public consumption may improve in the near future, however, pushback from proprietary trading firms is likely to delay or degrade any progressions towards fair and transparent markets.

Use the command 'dpotc' to display a barchart comparing dark pool (ATS) and OTC (Non ATS) volume. The raw data sets are available through the '--export' argument. Source: https://otctransparency.finra.org/otctransparency/

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
<img width="1400" alt="Feature Screenshot - dpotc Graph" src="https://user-images.githubusercontent.com/85772166/140554969-47e63298-6f25-4432-9795-7ee0d9870926.png">
<img width="1400" alt="Feature Screenshot - dpotc export" src="https://user-images.githubusercontent.com/85772166/140562944-c8b2c01a-ac74-44a0-904e-f6b3138bdf6c.png">

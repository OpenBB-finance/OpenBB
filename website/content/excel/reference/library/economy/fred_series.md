<!-- markdownlint-disable MD041 -->

Get data by series ID from FRED.

## Syntax

```excel wordwrap
=OBB.ECONOMY.FRED_SERIES(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fred, intrinio | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| limit | Number | The number of data entries to return. | True |
| frequency | Any | Frequency aggregation to convert high frequency data to lower frequency. None = No change a = Annual q = Quarterly m = Monthly w = Weekly d = Daily wef = Weekly, Ending Friday weth = Weekly, Ending Thursday wew = Weekly, Ending Wednesday wetu = Weekly, Ending Tuesday wem = Weekly, Ending Monday wesu = Weekly, Ending Sunday wesa = Weekly, Ending Saturday bwew = Biweekly, Ending Wednesday bwem = Biweekly, Ending Monday (provider: fred) | True |
| aggregation_method | Any | A key that indicates the aggregation method used for frequency aggregation. This parameter has no affect if the frequency parameter is not set. avg = Average sum = Sum eop = End of Period (provider: fred) | True |
| transform | Any | Transformation type None = No transformation chg = Change ch1 = Change from Year Ago pch = Percent Change pc1 = Percent Change from Year Ago pca = Compounded Annual Rate of Change cch = Continuously Compounded Rate of Change cca = Continuously Compounded Annual Rate of Change log = Natural Log (provider: fred) | True |
| all_pages | Boolean | Returns all pages of data from the API call at once. (provider: intrinio) | True |
| sleep | Number | Time to sleep between requests to avoid rate limiting. (provider: intrinio) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| value | Value of the index. (provider: intrinio) |

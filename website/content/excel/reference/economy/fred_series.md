---
title: FRED_SERIES
---

<!-- markdownlint-disable MD041 -->

Get data by series ID from FRED.

## Syntax

```excel wordwrap
=OBB.ECONOMY.FRED_SERIES(symbol;[start_date];[end_date];[limit];[provider];[frequency];[aggregation_method];[transform];[all_pages];[sleep])
```

### Example

```excel wordwrap
=OBB.ECONOMY.FRED_SERIES("GFDGDPA188S")
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **True** |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| limit | Number | The number of data entries to return. | False |
| provider | Text | Options: fred, intrinio, defaults to fred. | False |
| frequency | Any | Frequency aggregation to convert high frequency data to lower frequency. None = No change a = Annual q = Quarterly m = Monthly w = Weekly d = Daily wef = Weekly, Ending Friday weth = Weekly, Ending Thursday wew = Weekly, Ending Wednesday wetu = Weekly, Ending Tuesday wem = Weekly, Ending Monday wesu = Weekly, Ending Sunday wesa = Weekly, Ending Saturday bwew = Biweekly, Ending Wednesday bwem = Biweekly, Ending Monday (provider: fred) | False |
| aggregation_method | Any | A key that indicates the aggregation method used for frequency aggregation. This parameter has no affect if the frequency parameter is not set. avg = Average sum = Sum eop = End of Period (provider: fred) | False |
| transform | Any | Transformation type None = No transformation chg = Change ch1 = Change from Year Ago pch = Percent Change pc1 = Percent Change from Year Ago pca = Compounded Annual Rate of Change cch = Continuously Compounded Rate of Change cca = Continuously Compounded Annual Rate of Change log = Natural Log (provider: fred) | False |
| all_pages | Boolean | Returns all pages of data from the API call at once. (provider: intrinio) | False |
| sleep | Number | Time to sleep between requests to avoid rate limiting. (provider: intrinio) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| value | Value of the index. (provider: intrinio) |

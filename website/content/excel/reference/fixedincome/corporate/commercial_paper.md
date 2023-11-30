<!-- markdownlint-disable MD041 -->

Commercial Paper.  Commercial paper (CP) consists of short-term, promissory notes issued primarily by corporations. Maturities range up to 270 days but average about 30 days. Many companies use CP to raise cash needed for current transactions, and many find it to be a lower-cost alternative to bank loans.

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.COMMERCIAL_PAPER(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fred | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| maturity | string | The maturity. | true |
| category | string | The category. | true |
| grade | string | The grade. | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | Commercial Paper Rate.  |

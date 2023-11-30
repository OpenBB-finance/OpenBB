<!-- markdownlint-disable MD041 -->

Moody Corporate Bond Index.  Moody's Aaa and Baa are investment bonds that acts as an index of the performance of all bonds given an Aaa or Baa rating by Moody's Investors Service respectively. These corporate bonds often are used in macroeconomics as an alternative to the federal ten-year Treasury Bill as an indicator of the interest rate.

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.MOODY(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fred | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| index_type | string | The type of series. | true |
| spread | string | The type of spread. (provider: fred) | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | Moody Corporate Bond Index Rate.  |

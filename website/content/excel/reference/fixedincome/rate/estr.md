---
title: estr
description: Euro Short-Term Rate
keywords: 
- fixedincome
- rate
- estr
---

<!-- markdownlint-disable MD041 -->

Euro Short-Term Rate.  The euro short-term rate (€STR) reflects the wholesale euro unsecured overnight borrowing costs of banks located in the euro area. The €STR is published on each TARGET2 business day based on transactions conducted and settled on the previous TARGET2 business day (the reporting date “T”) with a maturity date of T+1 which are deemed to have been executed at arm’s length and thus reflect market rates in an unbiased way.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.RATE.ESTR([start_date];[end_date];[provider];[parameter])
```

### Example

```excel wordwrap
=OBB.FIXEDINCOME.RATE.ESTR()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| provider | Text | Options: fred, defaults to fred. | False |
| parameter | Text | Period of ESTR rate. (provider: fred) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | ESTR rate.  |

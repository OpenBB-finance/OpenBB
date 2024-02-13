---
title: estr
description: The euro short-term rate (€STR) reflects the wholesale euro unsecured overnight borrowing costs of banks located in the euro area
keywords:
- fixedincome
- estr
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /estr - Reference | OpenBB Terminal Docs" />

The euro short-term rate (€STR) reflects the wholesale euro unsecured overnight borrowing costs of banks located in the euro area. The €STR is published on each TARGET2 business day based on transactions conducted and settled on the previous TARGET2 business day (the reporting date “T”) with a maturity date of T+1 which are deemed to have been executed at arm’s length and thus reflect market rates in an unbiased way.

### Usage

```python wordwrap
estr [-p {volume_weighted_trimmed_mean_rate,number_of_transactions,number_of_active_banks,total_volume,share_of_volume_of_the_5_largest_active_banks,rate_at_75th_percentile_of_volume,rate_at_25th_percentile_of_volume}] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| parameter | -p  --parameter | Specific Euro Short-Term Rate data to retrieve | volume_weighted_trimmed_mean_rate | True | volume_weighted_trimmed_mean_rate, number_of_transactions, number_of_active_banks, total_volume, share_of_volume_of_the_5_largest_active_banks, rate_at_75th_percentile_of_volume, rate_at_25th_percentile_of_volume |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | None | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |

---

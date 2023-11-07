---
title: estr
description: "Detailed documentation page about the Euro Short-Term Rate (\u20ACSTR)\
  \ function, including its parameters, return values, and data structure."
keywords:
- Euro Short-Term Rate
- "\u20ACSTR"
- finance
- economic data
- SEO
- metadata
- functions
- parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.estr - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Euro Short-Term Rate.
    The euro short-term rate (€STR) reflects the wholesale euro unsecured overnight borrowing costs of banks located in
    the euro area. The €STR is published on each TARGET2 business day based on transactions conducted and settled on
    the previous TARGET2 business day (the reporting date “T”) with a maturity date of T+1 which are deemed to have been
    executed at arm’s length and thus reflect market rates in an unbiased way.

```python wordwrap
estr(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fred)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
| parameter | Literal['volume_weighted_trimmed_mean_rate', 'number_of_transactions', 'number_of_active_banks', 'total_volume', 'share_of_volume_of_the_5_largest_active_banks', 'rate_at_75th_percentile_of_volume', 'rate_at_25th_percentile_of_volume'] | Period of ESTR rate. | volume_weighted_trimmed_mean_rate | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[ESTR]
        Serializable results.

    provider : Optional[Literal['fred']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | ESTR rate. |
</TabItem>

</Tabs>

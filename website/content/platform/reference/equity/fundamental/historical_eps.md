---
title: historical_eps
description: Historical earnings-per-share for a given company
keywords:
- equity
- fundamental
- historical_eps
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity /fundamental/historical_eps - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Historical earnings-per-share for a given company.

```python wordwrap
obb.equity.fundamental.historical_eps(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| limit | int | The number of data entries to return. | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[HistoricalEps]
        Serializable results.

    provider : Optional[Literal['fmp']]
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
| symbol | str | Symbol representing the entity requested in the data. |
| announce_time | str | Timing of the earnings announcement. |
| eps_actual | float | Actual EPS from the earnings date. |
| eps_estimated | float | Estimated EPS for the earnings date. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| symbol | str | Symbol representing the entity requested in the data. |
| announce_time | str | Timing of the earnings announcement. |
| eps_actual | float | Actual EPS from the earnings date. |
| eps_estimated | float | Estimated EPS for the earnings date. |
| actual_eps | float | The actual earnings per share announced. |
| revenue_estimated | float | Estimated consensus revenue for the reporting period. |
| actual_revenue | float | The actual reported revenue. |
| reporting_time | str | The reporting time - e.g. after market close. |
| updated_at | date | The date when the data was last updated. |
| period_ending | date | The fiscal period end date. |
</TabItem>

</Tabs>


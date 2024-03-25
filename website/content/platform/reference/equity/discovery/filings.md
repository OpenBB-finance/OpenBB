---
title: "filings"
description: "Get the most-recent filings submitted to the SEC"
keywords:
- equity
- discovery
- filings
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/discovery/filings - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the URLs to SEC filings reported to EDGAR database, such as 10-K, 10-Q, 8-K, and more. SEC
filings include Form 10-K, Form 10-Q, Form 8-K, the proxy statement, Forms 3, 4, and 5, Schedule 13, Form 114,
Foreign Investment Disclosures and others. The annual 10-K report is required to be
filed annually and includes the company's financial statements, management discussion and analysis,
and audited financial statements.


Examples
--------

```python
from openbb import obb
obb.equity.discovery.filings(provider='fmp')
# Get filings for the year 2023, limited to 100 results
obb.equity.discovery.filings(start_date='2023-01-01', end_date='2023-12-31', limit=100, provider='fmp')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| form_type | str | Filter by form type. Visit https://www.sec.gov/forms for a list of supported form types. | None | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| form_type | str | Filter by form type. Visit https://www.sec.gov/forms for a list of supported form types. | None | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| is_done | bool | Flag for whether or not the filing is done. | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : DiscoveryFilings
        Serializable results.
    provider : Literal['fmp']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| cik | str | Central Index Key (CIK) for the requested entity. |
| title | str | Title of the filing. |
| date | datetime | The date of the data. |
| form_type | str | The form type of the filing |
| link | str | URL to the filing page on the SEC site. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| cik | str | Central Index Key (CIK) for the requested entity. |
| title | str | Title of the filing. |
| date | datetime | The date of the data. |
| form_type | str | The form type of the filing |
| link | str | URL to the filing page on the SEC site. |
</TabItem>

</Tabs>


---
title: filings
description: Learn how to get the most-recent SEC filings using the Python SDK. This
  page provides documentation for the `obb.equity.discovery.filings` method, along
  with its parameters and return values. Discover how to use the `start_date`, `end_date`,
  `form_type`, `limit`, and `provider` parameters to customize your query. Explore
  the `OBBject` and its properties such as `results`, `provider`, `warnings`, and
  `metadata`. Additionally, find details about the `timestamp`, `symbol`, `CIK`, `title`,
  `form_type`, and `URL` fields in the returned data. Start retrieving SEC filings
  easily with this comprehensive guide.
keywords:
- SEC filings
- most-recent filings
- Get filings
- Python SDK
- start_date parameter
- end_date parameter
- form_type parameter
- limit parameter
- provider parameter
- fmp provider
- is_done parameter
- OBBject
- results
- provider name
- warnings
- chart object
- metadata
- Data
- timestamp
- symbol
- CIK
- title
- form type
- URL
- is_done
---



<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the most-recent filings submitted to the SEC.

```python wordwrap
obb.equity.discovery.filings(start_date: Union[date, str] = None, end_date: Union[date, str] = None, form_type: str = None, limit: int = 100, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| form_type | str | Fuzzy filter by form type. E.g. 10-K, 10, 8, 6-K, etc. | None | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| form_type | str | Fuzzy filter by form type. E.g. 10-K, 10, 8, 6-K, etc. | None | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| is_done | Literal['true', 'false'] | Flag for whether or not the filing is done. | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[DiscoveryFilings]
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
| timestamp | datetime | The timestamp from when the filing was accepted. |
| symbol | str | Symbol representing the entity requested in the data. |
| cik | str | The CIK of the filing |
| title | str | The title of the filing |
| form_type | str | The form type of the filing |
| url | str | The URL of the filing |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| timestamp | datetime | The timestamp from when the filing was accepted. |
| symbol | str | Symbol representing the entity requested in the data. |
| cik | str | The CIK of the filing |
| title | str | The title of the filing |
| form_type | str | The form type of the filing |
| url | str | The URL of the filing |
| is_done | Literal['True', 'False'] | Whether or not the filing is done. |
</TabItem>

</Tabs>


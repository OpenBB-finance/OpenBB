---
title: fred_index
description: Documentation about Fred Historical function, a feature to retrieve historical
  close values for selected Fred indices. The page contains detailed parameters description
  and data structure including the provider, date range, limit, and symbol for data
  retrieval.
keywords:
- Fred Historical
- Fred indices
- Data retrieval
- Data API
- start_date
- end_date
- limit
- provider
- intrinio
- symbol
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fred_index - Economy - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# fred_index

Fred Historical. Historical close values for selected Fred indices.

```python wordwrap
fred_index(symbol: Union[str, List[str]], start_date: Union[date, str] = None, end_date: Union[date, str] = None, limit: int = 100, provider: Literal[str] = intrinio)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
| next_page | str | Token to get the next page of data from a previous API call. | None | True |
| all_pages | bool | Returns all pages of data from the API call at once. | False | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[FredHistorical]
        Serializable results.

    provider : Optional[Literal['intrinio']]
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
| value | float | Value of the index. |
</TabItem>

</Tabs>

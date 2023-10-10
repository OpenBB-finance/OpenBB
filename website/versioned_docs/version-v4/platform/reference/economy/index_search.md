---
title: index_search
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# index_search

Search for indices.

```python wordwrap
index_search(query: str, symbol: Union[bool, List[str]] = False, provider: Union[Literal[str]] = cboe)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| symbol | Union[bool, List[str]] | Whether to search by ticker symbol. | False | True |
| provider | Union[Literal['cboe']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| symbol | Union[bool, List[str]] | Whether to search by ticker symbol. | False | True |
| provider | Union[Literal['cboe']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| europe | bool | Filter for European indices. False for US indices. | False | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[IndexSearch]
        Serializable results.

    provider : Optional[Literal[Union[Literal['cboe'], NoneType]]
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
| symbol | str | Symbol of the index. |
| name | str | Name of the index. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol of the index. |
| name | str | Name of the index. |
| isin | Union[str] | ISIN code for the index. Valid only for European indices. |
| region | Union[str] | Region for the index. Valid only for European indices |
| description | Union[str] | Description for the index. |
| data_delay | Union[int] | Data delay for the index. Valid only for US indices. |
| currency | Union[str] | Currency for the index. |
| time_zone | Union[str] | Time zone for the index. Valid only for US indices. |
| open_time | Union[datetime.time] | Opening time for the index. Valid only for US indices. |
| close_time | Union[datetime.time] | Closing time for the index. Valid only for US indices. |
| tick_days | Union[str] | The trading days for the index. Valid only for US indices. |
| tick_frequency | Union[str] | Tick frequency for the index. Valid only for US indices. |
| tick_period | Union[str] | Tick period for the index. Valid only for US indices. |
</TabItem>

</Tabs>


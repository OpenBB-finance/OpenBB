---
title: globalnews
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# globalnews

Global News. Global news data.

```python wordwrap
globalnews(limit: int = 20, provider: Literal[str] = benzinga)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of articles to return. | 20 | True |
| provider | Literal['benzinga', 'fmp', 'intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of articles to return. | 20 | True |
| provider | Literal['benzinga', 'fmp', 'intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
| display | Literal['headline', 'abstract', 'full'] | Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). | full | True |
| date | str | Date of the news to retrieve. | None | True |
| start_date | str | Start date of the news to retrieve. | None | True |
| end_date | str | End date of the news to retrieve. | None | True |
| updated_since | int | Number of seconds since the news was updated. | None | True |
| published_since | int | Number of seconds since the news was published. | None | True |
| sort | Literal['id', 'created', 'updated'] | Key to sort the news by. | created | True |
| order | Literal['asc', 'desc'] | Order to sort the news by. | desc | True |
| isin | str | The ISIN of the news to retrieve. | None | True |
| cusip | str | The CUSIP of the news to retrieve. | None | True |
| channels | str | Channels of the news to retrieve. | None | True |
| topics | str | Topics of the news to retrieve. | None | True |
| authors | str | Authors of the news to retrieve. | None | True |
| content_types | str | Content types of the news to retrieve. | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[GlobalNews]
        Serializable results.

    provider : Optional[Literal['benzinga', 'fmp', 'intrinio']]
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
| date | datetime | Published date of the news. |
| title | str | Title of the news. |
| image | str | Image URL of the news. |
| text | str | Text/body of the news. |
| url | str | URL of the news. |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | Published date of the news. |
| title | str | Title of the news. |
| image | str | Image URL of the news. |
| text | str | Text/body of the news. |
| url | str | URL of the news. |
| id | str | ID of the news. |
| author | str | Author of the news. |
| teaser | str | Teaser of the news. |
| images | List[Dict[str, str]] | Images associated with the news. |
| channels | str | Channels associated with the news. |
| stocks | str | Stocks associated with the news. |
| tags | str | Tags associated with the news. |
| updated | datetime | None |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | Published date of the news. |
| title | str | Title of the news. |
| image | str | Image URL of the news. |
| text | str | Text/body of the news. |
| url | str | URL of the news. |
| site | str | Site of the news. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | Published date of the news. |
| title | str | Title of the news. |
| image | str | Image URL of the news. |
| text | str | Text/body of the news. |
| url | str | URL of the news. |
| id | str | Article ID. |
| company | Dict[str, Any] | Company details related to the news article. |
</TabItem>

</Tabs>


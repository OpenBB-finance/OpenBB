---
title: Company News
description: OpenBB Platform Data Model
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `CompanyNews` | `CompanyNewsQueryParams` | `CompanyNewsData` |

### Import Statement

```python
from openbb_core.provider.standard_models.company_news import (
CompanyNewsData,
CompanyNewsQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | str |  Here it is a separated list of symbols. |  | False |
| limit | int | The number of data entries to return. | 20 | True |
| provider | Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'ultima', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | str |  Here it is a separated list of symbols. |  | False |
| limit | int | The number of data entries to return. | 20 | True |
| provider | Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'ultima', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
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

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | str |  Here it is a separated list of symbols. |  | False |
| limit | int | The number of data entries to return. | 20 | True |
| provider | Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'ultima', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
| page | int | Page number of the results. Use in combination with limit. | 0 | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | str |  Here it is a separated list of symbols. |  | False |
| limit | int | The number of data entries to return. | 20 | True |
| provider | Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'ultima', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
| published_utc | str | Date query to fetch articles. Supports operators <, <=, >, >= | None | True |
| order | Literal['asc', 'desc'] | Sort order of the articles. | desc | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. Here it is the date of the news. |
| title | str | Title of the news. |
| image | str | Image URL of the news. |
| text | str | Text/body of the news. |
| url | str | URL of the news. |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. Here it is the date of the news. |
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
| updated | datetime | Updated date of the news. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. Here it is the date of the news. |
| title | str | Title of the news. |
| image | str | Image URL of the news. |
| text | str | Text/body of the news. |
| url | str | URL of the news. |
| symbol | str | Ticker of the fetched news. |
| site | str | Name of the news source. |
| images | Union[List[str], str] | URL to the images of the news. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. Here it is the date of the news. |
| title | str | Title of the news. |
| image | str | Image URL of the news. |
| text | str | Text/body of the news. |
| url | str | URL of the news. |
| id | str | Intrinio ID for the article. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. Here it is the date of the news. |
| title | str | Title of the news. |
| image | str | Image URL of the news. |
| text | str | Text/body of the news. |
| url | str | URL of the news. |
| amp_url | str | AMP URL. |
| author | str | Author of the article. |
| id | str | Article ID. |
| image_url | str | Image URL. |
| keywords | List[str] | Keywords in the article |
| publisher | openbb_polygon.models.company_news.PolygonPublisher | Publisher of the article. |
| tickers | List[str] | Tickers covered in the article. |
</TabItem>

<TabItem value='ultima' label='ultima'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. Here it is the date of the news. |
| title | str | Title of the news. |
| image | str | Image URL of the news. |
| text | str | Text/body of the news. |
| url | str | URL of the news. |
| publisher | str | Publisher of the news. |
| ticker | str | Ticker associated with the news. |
| riskCategory | str | Risk category of the news. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. Here it is the date of the news. |
| title | str | Title of the news. |
| image | str | Image URL of the news. |
| text | str | Text/body of the news. |
| url | str | URL of the news. |
| uuid | str | Unique identifier for the news article |
| publisher | str | Publisher of the news article |
| type | str | Type of the news article |
| thumbnail | List | Thumbnail related data to the ticker news article. |
| relatedTickers | str | Tickers related to the news article. |
</TabItem>

</Tabs>

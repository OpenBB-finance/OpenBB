---
title: Stock News
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `StockNews` | `StockNewsQueryParams` | `StockNewsData` |

### Import Statement

```python
from openbb_provider.standard_models.stock_news import (
StockNewsData,
StockNewsQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | str | Comma separated list of symbols. |  | False |
| limit | Union[typing_extensions.Annotated[int, Ge(ge=0)]] | Number of results to return per page. | 20 | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Union[Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | str | Comma separated list of symbols. |  | False |
| limit | Union[typing_extensions.Annotated[int, Ge(ge=0)]] | Number of results to return per page. | 20 | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Union[Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
| display | Literal['headline', 'abstract', 'full'] | Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). | full | True |
| date | Union[str] | Date of the news to retrieve. | None | True |
| start_date | Union[str] | Start date of the news to retrieve. | None | True |
| end_date | Union[str] | End date of the news to retrieve. | None | True |
| updated_since | Union[int] | Number of seconds since the news was updated. | None | True |
| published_since | Union[int] | Number of seconds since the news was published. | None | True |
| sort | Union[Literal['id', 'created', 'updated']] | Key to sort the news by. | created | True |
| order | Union[Literal['asc', 'desc']] | Order to sort the news by. | desc | True |
| isin | Union[str] | The ISIN of the news to retrieve. | None | True |
| cusip | Union[str] | The CUSIP of the news to retrieve. | None | True |
| channels | Union[str] | Channels of the news to retrieve. | None | True |
| topics | Union[str] | Topics of the news to retrieve. | None | True |
| authors | Union[str] | Authors of the news to retrieve. | None | True |
| content_types | Union[str] | Content types of the news to retrieve. | None | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | str | Comma separated list of symbols. |  | False |
| limit | Union[typing_extensions.Annotated[int, Ge(ge=0)]] | Number of results to return per page. | 20 | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Union[Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
| published_utc | Union[str] | Date query to fetch articles. Supports operators <, <=, >, >= | None | True |
| order | Union[Literal['asc', 'desc']] | Sort order of the articles. | desc | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | Published date of the news. |
| title | str | Title of the news. |
| image | Union[str] | Image URL of the news. |
| text | Union[str] | Text/body of the news. |
| url | str | URL of the news. |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | Published date of the news. |
| title | str | Title of the news. |
| image | Union[str] | Image URL of the news. |
| text | Union[str] | Text/body of the news. |
| url | str | URL of the news. |
| id | str | ID of the news. |
| author | Union[str] | Author of the news. |
| teaser | Union[str] | Teaser of the news. |
| images | Union[List[Dict[str, str]]] | Images associated with the news. |
| channels | Union[str] | Channels associated with the news. |
| stocks | Union[str] | Stocks associated with the news. |
| tags | Union[str] | Tags associated with the news. |
| updated | Union[datetime] | None |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | Published date of the news. |
| title | str | Title of the news. |
| image | Union[str] | Image URL of the news. |
| text | Union[str] | Text/body of the news. |
| url | str | URL of the news. |
| symbol | str | Ticker of the fetched news. |
| site | str | Name of the news source. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | Published date of the news. |
| title | str | Title of the news. |
| image | Union[str] | Image URL of the news. |
| text | Union[str] | Text/body of the news. |
| url | str | URL of the news. |
| id | str | Intrinio ID for the article. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | Published date of the news. |
| title | str | Title of the news. |
| image | Union[str] | Image URL of the news. |
| text | Union[str] | Text/body of the news. |
| url | str | URL of the news. |
| amp_url | Union[str] | AMP URL. |
| author | Union[str] | Author of the article. |
| id | str | Article ID. |
| image_url | Union[str] | Image URL. |
| keywords | Union[List[str]] | Keywords in the article |
| publisher | openbb_polygon.models.stock_news.PolygonPublisher | Publisher of the article. |
| tickers | List[str] | Tickers covered in the article. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | Published date of the news. |
| title | str | Title of the news. |
| image | Union[str] | Image URL of the news. |
| text | Union[str] | Text/body of the news. |
| url | str | URL of the news. |
| uuid | str | Unique identifier for the news article |
| publisher | str | Publisher of the news article |
| type | str | Type of the news article |
| thumbnail | Union[List] | Thumbnail related data to the ticker news article. |
| relatedTickers | str | Tickers related to the news article. |
</TabItem>

</Tabs>


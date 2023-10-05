---
title: StockNews
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | str | Symbol to get data for. |  | False |
| page | int | Page of the stock news to be retrieved. | 0 | True |
| limit | NonNegativeInt | Number of results to return per page. | 15 | True |
| provider | Literal['benzinga', 'fmp', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| displayOutput | Literal['headline', 'summary', 'full', 'all'] | Type of data to return. | headline | True |
| date | datetime | Date of the news to retrieve. | None | True |
| dateFrom | datetime | Start date of the news to retrieve. | None | True |
| dateTo | datetime | End date of the news to retrieve. | None | True |
| updatedSince | int | Number of seconds since the news was updated. | None | True |
| publishedSince | int | Number of seconds since the news was published. | None | True |
| sort | Literal['published_at', 'updated_at', 'title', 'author', 'channel', 'ticker', 'topic', 'content_type'] | Order in which to sort the news. Options are: published_at, updated_at, title, author, channel, ticker, topic, content_type. | None | True |
| isin | str | The ISIN of the news to retrieve. | None | True |
| cusip | str | The CUSIP of the news to retrieve. | None | True |
| channels | str | Channels of the news to retrieve. | None | True |
| topics | str | Topics of the news to retrieve. | None | True |
| authors | str | Authors of the news to retrieve. | None | True |
| content_types | str | Content types of the news to retrieve. | None | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| ticker_lt | str | Less than, by default None | None | True |
| ticker_lte | str | Less than or equal, by default None | None | True |
| ticker_gt | str | Greater than, by default None | None | True |
| ticker_gte | str | Greater than or equal, by default None | None | True |
| published_utc | str | Published date of the query, by default None | None | True |
| published_utc_lt | str | Less than, by default None | None | True |
| published_utc_lte | str | Less than or equal, by default None | None | True |
| published_utc_gt | str | Greater than, by default None | None | True |
| published_utc_gte | str | Greater than or equal, by default None | None | True |
| order | Literal['asc', 'desc'] | Sort order of the query, by default None | None | True |
| sort | str | Sort of the query, by default None | None | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | Published date of the news. |
| title | str | Title of the news. |
| text | str | Text/body of the news. |
| url | str | URL of the news. |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| images | List[openbb_benzinga.utils.helpers.BenzingaImage] | Images associated with the news. |
| channels | List[str] | Channels associated with the news. |
| stocks | List[str] | Stocks associated with the news. |
| tags | List[str] | Tags associated with the news. |
| teaser | str | Teaser of the news. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Ticker of the fetched news. |
| image | str | URL to the image of the news source. |
| site | str | Name of the news source. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| amp_url | str | AMP URL. |
| author | str | Author of the article. |
| id | str | Article ID. |
| image_url | str | Image URL. |
| keywords | List[str] | Keywords in the article |
| publisher | openbb_polygon.models.stock_news.PolygonPublisher | Publisher of the article. |
| tickers | List[str] | Tickers covered in the article. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| uuid | str | Unique identifier for the news article |
| publisher | str | Publisher of the news article |
| type | str | Type of the news article |
| thumbnail | Dict[str, Any] | Thumbnail related data to the ticker news article. |
| relatedTickers | str | Tickers related to the news article. |
</TabItem>

</Tabs>


---
title: GlobalNews
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
| page | NonNegativeInt | Page of the global news. | 0 | True |
| provider | Literal['benzinga', 'fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| pageSize | int | Number of results to return per page. | 15 | True |
| displayOutput | Literal['headline', 'summary', 'full', 'all'] | Type of data to return. | headline | True |
| date | datetime | Date of the news to retrieve. | None | True |
| dateFrom | datetime | Start date of the news to retrieve. | None | True |
| dateTo | datetime | End date of the news to retrieve. | None | True |
| updatedSince | int | Number of seconds since the news was updated. | None | True |
| publishedSince | int | Number of seconds since the news was published. | None | True |
| sort | Literal['published_at', 'updated_at', 'title', 'author', 'channel', 'ticker', 'topic', 'content_type'] | Order in which to sort the news.  | None | True |
| isin | str | The ISIN of the news to retrieve. | None | True |
| cusip | str | The CUSIP of the news to retrieve. | None | True |
| tickers | str | Tickers of the news to retrieve. | None | True |
| channels | str | Channels of the news to retrieve. | None | True |
| topics | str | Topics of the news to retrieve. | None | True |
| authors | str | Authors of the news to retrieve. | None | True |
| content_types | str | Content types of the news to retrieve. | None | True |
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
| site | str | Site of the news. |
</TabItem>

</Tabs>


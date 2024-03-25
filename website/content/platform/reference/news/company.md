---
title: "company"
description: "Get company news for one or more companies using various providers. This  API allows you to retrieve news articles along with metadata such as date, title,  image, text, and URL. The available providers include Benzinga, FMP, Intrinio, Polygon,  Ultima, and Yfinance."
keywords:
- company news
- news for companies
- news API
- API parameters
- benzinga provider
- fmp provider
- polygon provider
- intrinio provider
- ultima provider
- yfinance provider
- data entries
- metadata
- company news results
- company news warnings
- company news chart
- data date
- data title
- data image
- data text
- data URL
- benzinga data
- fmp data
- intrinio data
- polygon data
- ultima data
- yfinance data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="news/company - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Company News. Get news for one or more companies.


Examples
--------

```python
from openbb import obb
obb.news.company(provider='benzinga')
obb.news.company(limit=100, provider='benzinga')
# Get news on the specified dates.
obb.news.company(symbol='AAPL', start_date='2024-02-01', end_date='2024-02-07', provider='intrinio')
# Display the headlines of the news.
obb.news.company(symbol='AAPL', display=headline, provider='benzinga')
# Get news for multiple symbols.
obb.news.company(symbol='aapl,tsla', provider='fmp')
# Get news company's ISIN.
obb.news.company(symbol='NVDA', isin=US0378331005, provider='benzinga')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): benzinga, fmp, intrinio, polygon, tiingo, tmx, yfinance. | None | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 2500 | True |
| provider | Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): benzinga, fmp, intrinio, polygon, tiingo, tmx, yfinance. | None | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 2500 | True |
| provider | Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
| date | Union[date, str] | A specific date to get data for. | None | True |
| display | Literal['headline', 'abstract', 'full'] | Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). | full | True |
| updated_since | int | Number of seconds since the news was updated. | None | True |
| published_since | int | Number of seconds since the news was published. | None | True |
| sort | Literal['id', 'created', 'updated'] | Key to sort the news by. | created | True |
| order | Literal['asc', 'desc'] | Order to sort the news by. | desc | True |
| isin | str | The company's ISIN. | None | True |
| cusip | str | The company's CUSIP. | None | True |
| channels | str | Channels of the news to retrieve. | None | True |
| topics | str | Topics of the news to retrieve. | None | True |
| authors | str | Authors of the news to retrieve. | None | True |
| content_types | str | Content types of the news to retrieve. | None | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): benzinga, fmp, intrinio, polygon, tiingo, tmx, yfinance. | None | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 2500 | True |
| provider | Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
| page | int | Page number of the results. Use in combination with limit. | 0 | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): benzinga, fmp, intrinio, polygon, tiingo, tmx, yfinance. | None | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 2500 | True |
| provider | Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): benzinga, fmp, intrinio, polygon, tiingo, tmx, yfinance. | None | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 2500 | True |
| provider | Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
| order | Literal['asc', 'desc'] | Sort order of the articles. | desc | True |
</TabItem>

<TabItem value='tiingo' label='tiingo'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): benzinga, fmp, intrinio, polygon, tiingo, tmx, yfinance. | None | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 2500 | True |
| provider | Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
| offset | int | Page offset, used in conjunction with limit. | 0 | True |
| source | str | A comma-separated list of the domains requested. | None | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): benzinga, fmp, intrinio, polygon, tiingo, tmx, yfinance. | None | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 2500 | True |
| provider | Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
| page | int | The page number to start from. Use with limit. | 1 | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): benzinga, fmp, intrinio, polygon, tiingo, tmx, yfinance. | None | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 2500 | True |
| provider | Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : CompanyNews
        Serializable results.
    provider : Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'yfinance']
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
| date | datetime | The date of the data. Here it is the published date of the article. |
| title | str | Title of the article. |
| text | str | Text/body of the article. |
| images | List[Dict[str, str]] | Images associated with the article. |
| url | str | URL to the article. |
| symbols | str | Symbols associated with the article. |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. Here it is the published date of the article. |
| title | str | Title of the article. |
| text | str | Text/body of the article. |
| images | List[Dict[str, str]] | Images associated with the article. |
| url | str | URL to the article. |
| symbols | str | Symbols associated with the article. |
| id | str | Article ID. |
| author | str | Author of the article. |
| teaser | str | Teaser of the news. |
| channels | str | Channels associated with the news. |
| stocks | str | Stocks associated with the news. |
| tags | str | Tags associated with the news. |
| updated | datetime | Updated date of the news. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. Here it is the published date of the article. |
| title | str | Title of the article. |
| text | str | Text/body of the article. |
| images | List[Dict[str, str]] | Images associated with the article. |
| url | str | URL to the article. |
| symbols | str | Symbols associated with the article. |
| source | str | Name of the news source. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. Here it is the published date of the article. |
| title | str | Title of the article. |
| text | str | Text/body of the article. |
| images | List[Dict[str, str]] | Images associated with the article. |
| url | str | URL to the article. |
| symbols | str | Symbols associated with the article. |
| id | str | Article ID. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. Here it is the published date of the article. |
| title | str | Title of the article. |
| text | str | Text/body of the article. |
| images | List[Dict[str, str]] | Images associated with the article. |
| url | str | URL to the article. |
| symbols | str | Symbols associated with the article. |
| source | str | Source of the article. |
| tags | str | Keywords/tags in the article |
| id | str | Article ID. |
| amp_url | str | AMP URL. |
| publisher | openbb_polygon.models.company_news.PolygonPublisher | Publisher of the article. |
</TabItem>

<TabItem value='tiingo' label='tiingo'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. Here it is the published date of the article. |
| title | str | Title of the article. |
| text | str | Text/body of the article. |
| images | List[Dict[str, str]] | Images associated with the article. |
| url | str | URL to the article. |
| symbols | str | Symbols associated with the article. |
| tags | str | Tags associated with the news article. |
| article_id | int | Unique ID of the news article. |
| source | str | News source. |
| crawl_date | datetime | Date the news article was crawled. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. Here it is the published date of the article. |
| title | str | Title of the article. |
| text | str | Text/body of the article. |
| images | List[Dict[str, str]] | Images associated with the article. |
| url | str | URL to the article. |
| symbols | str | Symbols associated with the article. |
| source | str | Source of the news. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. Here it is the published date of the article. |
| title | str | Title of the article. |
| text | str | Text/body of the article. |
| images | List[Dict[str, str]] | Images associated with the article. |
| url | str | URL to the article. |
| symbols | str | Symbols associated with the article. |
| source | str | Source of the news article |
</TabItem>

</Tabs>


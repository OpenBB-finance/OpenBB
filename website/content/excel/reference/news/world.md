---
title: world
description: Learn how to retrieve global news data using the obb.news.world API.
  This documentation covers the parameters, returns, and data structures used in the
  API, including details on how to set the limit and provider, and how to filter the
  news by date, author, channels, and more. Explore the different data fields such
  as date, title, images, text, and URL, and understand the structure of the returned
  results, warnings, chart, and metadata.
keywords: 
- Global News
- global news data
- obb.news.world
- parameters
- limit
- provider
- default
- benzinga
- biztoc
- fmp
- intrinio
- display
- date
- start_date
- end_date
- updated_since
- published_since
- sort
- order
- isin
- cusip
- channels
- topics
- authors
- content_types
- returns
- results
- provider
- warnings
- chart
- metadata
- data
- date
- title
- images
- text
- url
- id
- author
- teaser
- stocks
- tags
- updated
- favicon
- score
- site
- company
- datetime
- list
- dict
---

<!-- markdownlint-disable MD041 -->

World News. Global news data.

```excel wordwrap
=OBB.NEWS.WORLD(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: benzinga, fmp, intrinio, tiingo | true |
| limit | number | The number of data entries to return. Here its the no. of articles to return. | true |
| display | string | Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). (provider: benzinga) | true |
| date | string | Date of the news to retrieve. (provider: benzinga) | true |
| start_date | string | Start date of the news to retrieve. (provider: benzinga) | true |
| end_date | string | End date of the news to retrieve. (provider: benzinga) | true |
| updated_since | number | Number of seconds since the news was updated. (provider: benzinga) | true |
| published_since | number | Number of seconds since the news was published. (provider: benzinga) | true |
| sort | string | Key to sort the news by. (provider: benzinga) | true |
| order | string | Order to sort the news by. (provider: benzinga) | true |
| isin | string | The ISIN of the news to retrieve. (provider: benzinga) | true |
| cusip | string | The CUSIP of the news to retrieve. (provider: benzinga) | true |
| channels | string | Channels of the news to retrieve. (provider: benzinga) | true |
| topics | string | Topics of the news to retrieve. (provider: benzinga) | true |
| authors | string | Authors of the news to retrieve. (provider: benzinga) | true |
| content_types | string | Content types of the news to retrieve. (provider: benzinga) | true |
| source | string | A comma-separated list of the domains requested. (provider: tiingo) | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data. Here it is the published date of the news.  |
| title | Title of the news.  |
| images | Images associated with the news.  |
| text | Text/body of the news.  |
| url | URL of the news.  |
| id | ID of the news. (provider: benzinga);
    Article ID. (provider: intrinio) |
| author | Author of the news. (provider: benzinga) |
| teaser | Teaser of the news. (provider: benzinga) |
| channels | Channels associated with the news. (provider: benzinga) |
| stocks | Stocks associated with the news. (provider: benzinga) |
| tags | Tags associated with the news. (provider: benzinga, tiingo) |
| updated | Updated date of the news. (provider: benzinga) |
| site | Site of the news. (provider: fmp);
    Name of the news source. (provider: tiingo) |
| company | Company details related to the news article. (provider: intrinio) |
| symbols | Ticker tagged in the fetched news. (provider: tiingo) |
| article_id | Unique ID of the news article. (provider: tiingo) |
| crawl_date | Date the news article was crawled. (provider: tiingo) |

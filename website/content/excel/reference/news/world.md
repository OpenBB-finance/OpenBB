---
title: WORLD
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

## Syntax

```excel wordwrap
=OBB.NEWS.WORLD([limit];[provider];[display];[date];[start_date];[end_date];[updated_since];[published_since];[sort];[order];[isin];[cusip];[channels];[topics];[authors];[content_types];[source])
```

### Example

```excel wordwrap
=OBB.NEWS.WORLD()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| limit | Number | The number of data entries to return. Here its the no. of articles to return. | False |
| provider | Text | Options: benzinga, fmp, intrinio, tiingo, defaults to benzinga. | False |
| display | Text | Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). (provider: benzinga) | False |
| date | Text | Date of the news to retrieve. (provider: benzinga) | False |
| start_date | Text | Start date of the news to retrieve. (provider: benzinga) | False |
| end_date | Text | End date of the news to retrieve. (provider: benzinga) | False |
| updated_since | Number | Number of seconds since the news was updated. (provider: benzinga) | False |
| published_since | Number | Number of seconds since the news was published. (provider: benzinga) | False |
| sort | Text | Key to sort the news by. (provider: benzinga) | False |
| order | Text | Order to sort the news by. (provider: benzinga) | False |
| isin | Text | The ISIN of the news to retrieve. (provider: benzinga) | False |
| cusip | Text | The CUSIP of the news to retrieve. (provider: benzinga) | False |
| channels | Text | Channels of the news to retrieve. (provider: benzinga) | False |
| topics | Text | Topics of the news to retrieve. (provider: benzinga) | False |
| authors | Text | Authors of the news to retrieve. (provider: benzinga) | False |
| content_types | Text | Content types of the news to retrieve. (provider: benzinga) | False |
| source | Text | A comma-separated list of the domains requested. (provider: tiingo) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data. Here it is the published date of the news.  |
| title | Title of the news.  |
| images | Images associated with the news.  |
| text | Text/body of the news.  |
| url | URL of the news.  |
| id | Article ID. (provider: benzinga, intrinio) |
| author | Author of the news. (provider: benzinga) |
| teaser | Teaser of the news. (provider: benzinga) |
| channels | Channels associated with the news. (provider: benzinga) |
| stocks | Stocks associated with the news. (provider: benzinga) |
| tags | Tags associated with the news. (provider: benzinga, tiingo) |
| updated | Updated date of the news. (provider: benzinga) |
| site | News source. (provider: fmp, tiingo) |
| company | Company details related to the news article. (provider: intrinio) |
| symbols | Ticker tagged in the fetched news. (provider: tiingo) |
| article_id | Unique ID of the news article. (provider: tiingo) |
| crawl_date | Date the news article was crawled. (provider: tiingo) |

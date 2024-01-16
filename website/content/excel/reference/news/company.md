---
title: company
description: Get company news for one or more companies using various providers. This
  API allows you to retrieve news articles along with metadata such as date, title,
  image, text, and URL. The available providers include Benzinga, FMP, Intrinio, Polygon,
  Ultima, and Yfinance.
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

<!-- markdownlint-disable MD041 -->

Company News. Get news for one or more companies.

## Syntax

```excel wordwrap
=OBB.NEWS.COMPANY(symbols;[limit];[provider];[display];[date];[start_date];[end_date];[updated_since];[published_since];[sort];[order];[isin];[cusip];[channels];[topics];[authors];[content_types];[page];[published_utc];[source])
```

### Example

```excel wordwrap
=OBB.NEWS.COMPANY("AAPL,MSFT")
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| **symbols** | **Text** | **Here it is a separated list of symbols.** | **True** |
| limit | Number | The number of data entries to return. | False |
| provider | Text | Options: benzinga, fmp, intrinio, polygon, tiingo, defaults to benzinga. | False |
| display | Text | Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). (provider: benzinga) | False |
| date | Text | Date of the news to retrieve. (provider: benzinga) | False |
| start_date | Text | Start date of the news to retrieve. (provider: benzinga) | False |
| end_date | Text | End date of the news to retrieve. (provider: benzinga) | False |
| updated_since | Number | Number of seconds since the news was updated. (provider: benzinga) | False |
| published_since | Number | Number of seconds since the news was published. (provider: benzinga) | False |
| sort | Text | Key to sort the news by. (provider: benzinga) | False |
| order | Text | Order to sort the news by. (provider: benzinga); Sort order of the articles. (provider: polygon) | False |
| isin | Text | The ISIN of the news to retrieve. (provider: benzinga) | False |
| cusip | Text | The CUSIP of the news to retrieve. (provider: benzinga) | False |
| channels | Text | Channels of the news to retrieve. (provider: benzinga) | False |
| topics | Text | Topics of the news to retrieve. (provider: benzinga) | False |
| authors | Text | Authors of the news to retrieve. (provider: benzinga) | False |
| content_types | Text | Content types of the news to retrieve. (provider: benzinga) | False |
| page | Number | Page number of the results. Use in combination with limit. (provider: fmp) | False |
| published_utc | Text | Date query to fetch articles. Supports operators <, <=, >, >= (provider: polygon) | False |
| source | Text | A comma-separated list of the domains requested. (provider: tiingo) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbols |  Here it is a separated list of symbols.  |
| date | The date of the data. Here it is the date of the news.  |
| title | Title of the news.  |
| image | Image URL of the news.  |
| text | Text/body of the news.  |
| url | URL of the news.  |
| id | Article ID. (provider: benzinga, intrinio, polygon) |
| author | Author of the article. (provider: benzinga, polygon) |
| teaser | Teaser of the news. (provider: benzinga) |
| images | URL to the images of the news. (provider: benzinga, fmp) |
| channels | Channels associated with the news. (provider: benzinga) |
| stocks | Stocks associated with the news. (provider: benzinga) |
| tags | Tags associated with the news. (provider: benzinga, tiingo) |
| updated | Updated date of the news. (provider: benzinga) |
| site | Name of the news source. (provider: fmp);     News source. (provider: tiingo) |
| amp_url | AMP URL. (provider: polygon) |
| image_url | Image URL. (provider: polygon) |
| keywords | Keywords in the article (provider: polygon) |
| publisher | Publisher of the article. (provider: polygon) |
| article_id | Unique ID of the news article. (provider: tiingo) |
| crawl_date | Date the news article was crawled. (provider: tiingo) |

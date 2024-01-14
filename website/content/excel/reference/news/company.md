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

```jsx<span style={color: 'red'}>=OBB.NEWS.COMPANY(symbols;[provider];[limit];[display];[date];[start_date];[end_date];[updated_since];[published_since];[sort];[order];[isin];[cusip];[channels];[topics];[authors];[content_types];[page];[published_utc];[source])</span>```

### Example

```excel wordwrap
=OBB.NEWS.COMPANY("AAPL,MSFT")
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| **symbols** | **Text** | **Here it is a separated list of symbols.** | **False** |
| provider | Text | Options: benzinga, fmp, intrinio, polygon, tiingo, defaults to benzinga. | True |
| limit | Number | The number of data entries to return. | True |
| display | Text | Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). (provider: benzinga) | True |
| date | Text | Date of the news to retrieve. (provider: benzinga) | True |
| start_date | Text | Start date of the news to retrieve. (provider: benzinga) | True |
| end_date | Text | End date of the news to retrieve. (provider: benzinga) | True |
| updated_since | Number | Number of seconds since the news was updated. (provider: benzinga) | True |
| published_since | Number | Number of seconds since the news was published. (provider: benzinga) | True |
| sort | Text | Key to sort the news by. (provider: benzinga) | True |
| order | Text | Order to sort the news by. (provider: benzinga); Sort order of the articles. (provider: polygon) | True |
| isin | Text | The ISIN of the news to retrieve. (provider: benzinga) | True |
| cusip | Text | The CUSIP of the news to retrieve. (provider: benzinga) | True |
| channels | Text | Channels of the news to retrieve. (provider: benzinga) | True |
| topics | Text | Topics of the news to retrieve. (provider: benzinga) | True |
| authors | Text | Authors of the news to retrieve. (provider: benzinga) | True |
| content_types | Text | Content types of the news to retrieve. (provider: benzinga) | True |
| page | Number | Page number of the results. Use in combination with limit. (provider: fmp) | True |
| published_utc | Text | Date query to fetch articles. Supports operators <, <=, >, >= (provider: polygon) | True |
| source | Text | A comma-separated list of the domains requested. (provider: tiingo) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data. Here it is the date of the news.  |
| title | Title of the news.  |
| image | Image URL of the news.  |
| text | Text/body of the news.  |
| url | URL of the news.  |
| id | ID of the news. (provider: benzinga);     Intrinio ID for the article. (provider: intrinio);     Article ID. (provider: polygon) |
| author | Author of the news. (provider: benzinga);     Author of the article. (provider: polygon) |
| teaser | Teaser of the news. (provider: benzinga) |
| images | Images associated with the news. (provider: benzinga);     URL to the images of the news. (provider: fmp) |
| channels | Channels associated with the news. (provider: benzinga) |
| stocks | Stocks associated with the news. (provider: benzinga) |
| tags | Tags associated with the news. (provider: benzinga, tiingo) |
| updated | Updated date of the news. (provider: benzinga) |
| symbol | Ticker of the fetched news. (provider: fmp) |
| site | Name of the news source. (provider: fmp, tiingo) |
| amp_url | AMP URL. (provider: polygon) |
| image_url | Image URL. (provider: polygon) |
| keywords | Keywords in the article (provider: polygon) |
| publisher | Publisher of the article. (provider: polygon, yfinance) |
| tickers | Tickers covered in the article. (provider: polygon) |
| symbols | Ticker tagged in the fetched news. (provider: tiingo) |
| article_id | Unique ID of the news article. (provider: tiingo) |
| crawl_date | Date the news article was crawled. (provider: tiingo) |
| uuid | Unique identifier for the news article (provider: yfinance) |
| type | Type of the news article (provider: yfinance) |
| thumbnail | Thumbnail related data to the ticker news article. (provider: yfinance) |
| related_tickers | Tickers related to the news article. (provider: yfinance) |

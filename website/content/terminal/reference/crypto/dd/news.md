---
title: news
description: OpenBB Terminal Function
---

# news

Display most recent news on the given coin from CryptoPanic aggregator platform. [Source: https://cryptopanic.com/]

### Usage

```python
news [-l LIMIT] [-k {news,media}] [--filter {rising,hot,bullish,bearish,important,saved,lol}] [-r {en,de,es,fr,nl,it,pt,ru}] [-s {published_at,domain,title,negative_votes,positive_votes}] [--reverse] [-u]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records | 10 | True | None |
| kind | Filter by category of news. Available values: news or media. | news | True | news, media |
| filter | Filter by kind of news. From: rising|hot|bullish|bearish|important|saved|lol | None | True | rising, hot, bullish, bearish, important, saved, lol |
| region | Filter news by regions. Available regions are: en (English), de (Deutsch), nl (Dutch), es (Español), fr (Français), it (Italiano), pt (Português), ru (Русский) | en | True | en, de, es, fr, nl, it, pt, ru |
| sortby | Sort by given column. Default: published_at | published_at | True | published_at, domain, title, negative_votes, positive_votes |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| urls | Flag to disable urls. Hides column with URL. | True | True | None |


---

## Examples

```python
2022 Apr 25, 09:49 (🦋) /crypto/dd/ $ news
                                             Most Recent News
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ published_at ┃ title                                       ┃ link                                       ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2022-04-24   │ Major German Bank Applies For Crypto        │ https://cryptopanic.com/news/15005355/Maj… │
│              │ Custody License                             │                                            │
├──────────────┼─────────────────────────────────────────────┼────────────────────────────────────────────┤
│ 2022-04-24   │ These Two Companies Will Let You Buy a      │ https://cryptopanic.com/news/15005488/The… │
│              │ House with Crypto                           │                                            │
├──────────────┼─────────────────────────────────────────────┼────────────────────────────────────────────
```
---

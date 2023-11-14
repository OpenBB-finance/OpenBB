---
title: cnews
description: cnews page provides an interface to access customized news from various
  sectors such as crypto, buybacks, politics, healthcare, and many more, sourced from
  Seeking Alpha. Users can limit the number of news displayed and select specific
  news type for display.
keywords:
- cnews
- customized news
- Seeking Alpha
- top-news
- crypto
- issuance
- buybacks
- commodities
- spacs
- politics
- consumer
- energy
- financials
- healthcare
- mlps
- reits
- technology
- stock repurchase program
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/disc/cnews - Reference | OpenBB Terminal Docs" />

Customized news. [Source: Seeking Alpha]

### Usage

```python
cnews [-t {top-news,on-the-move,market-pulse,notable-calls,buybacks,commodities,crypto,issuance,global,guidance,ipos,spacs,politics,m-a,consumer,energy,financials,healthcare,mlps,reits,technology}] [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| s_type | number of news to display | Top-News | True | top-news, on-the-move, market-pulse, notable-calls, buybacks, commodities, crypto, issuance, global, guidance, ipos, spacs, politics, m-a, consumer, energy, financials, healthcare, mlps, reits, technology |
| limit | limit of news to display | 5 | True | None |


---

## Examples

```python
2022 Feb 16, 03:52 (🦋) /stocks/disc/ $ cnews
2022-02-15 19:04:21 - 3800509 - ViacomCBS earnings call: A flood of content feeding transformation to Paramount
https://seekingalpha.com/news/3800509-viacomcbs-earnings-call-a-flood-of-content-feeding-transformation-to-paramount

2022-02-15 16:26:46 - 3800415 - ViacomCBS rebranding company as Paramount Global
https://seekingalpha.com/news/3800415-viacomcbs-rebranding-company-as-paramount-global

2022-02-15 16:25:33 - 3800411 - Airbnb stock soars after guidance comes in strong
https://seekingalpha.com/news/3800411-airbnb-stock-soars-after-guidance-comes-in-strong

2022-02-15 16:25:05 - 3800410 - ViacomCBS rebranding company as Paramount Global
https://seekingalpha.com/news/3800410-viacomcbs-rebranding-company-as-paramount-global

2022-02-15 16:14:45 - 3800380 - ViacomCBS dips as profits dip despite revenue beat, streaming gains
https://seekingalpha.com/news/3800380-viacomcbs-dips-as-profits-dip-despite-revenue-beat-streaming-gains

2022-02-15 16:14:20 - 3800378 - Wynn Resorts trades lower after earnings, Encore Boston sale
https://seekingalpha.com/news/3800378-wynn-resorts-trades-lower-after-earnings-encore-boston-sale

2022 Feb 16, 03:52 (🦋) /stocks/disc/ $ cnews -t buybacks
2022-02-15 16:24:36 - 3800409 - DHI launches new $15M in stock repurchase program
https://seekingalpha.com/news/3800409-dhi-launches-new-15m-in-stock-repurchase-program

2022-02-15 16:20:21 - 3800395 - Upstart stock soars after Q4 earnings beat, strong guidance, stock buyback
https://seekingalpha.com/news/3800395-upstart-stock-soars-after-q4-earnings-beat-strong-guidance-stock-buyback

2022-02-15 16:17:07 - 3800387 - Upstart announces $400M share repurchase program
https://seekingalpha.com/news/3800387-upstart-announces-400m-share-repurchase-program

2022-02-15 08:04:55 - 3800026 - GCM Grosvenor reports Q4 results, increases stock repurchase plan by $20M
https://seekingalpha.com/news/3800026-gcm-grosvenor-reports-q4-results-increases-stock-repurchase-plan-by-20m

2022-02-15 08:04:08 - 3800020 - Middlefield Banc declares $0.17 dividend; expands stock buyback plan
https://seekingalpha.com/news/3800020-middlefield-banc-corp-declares-0_17-dividend

2022-02-15 07:26:40 - 3799989 - LGI Homes expands stock repurchase program by $200M
https://seekingalpha.com/news/3799989-lgi-homes-expands-stock-repurchase-program-by-200m
```
---

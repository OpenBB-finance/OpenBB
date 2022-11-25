---
title: trending
description: OpenBB Terminal Function
---

# trending

Trending news articles. [Source: Seeking Alpha]

### Usage

```python
trending [-i N_ID] [-l LIMIT] [-d S_DATE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_id | article ID | -1 | True | None |
| limit | limit of articles being printed | 5 | True | None |
| s_date | starting date of articles | 2022-11-25 | True | None |


---

## Examples

```python
2022 Feb 16, 04:13 (🦋) /stocks/disc/ $ trending -i 10
2010-03-21 08:33:21   Deutsche Bank's Marc Greenberg can't justify the BUD deal. But he says Bud Light Lime is the...
https://seekingalpha.com/news/10

 Deutsche Bank's Marc Greenberg can't justify the BUD deal. But he says Bud Light Lime is the beer to beat.
2022 Feb 16, 04:13 (🦋) /stocks/disc/ $ trending -l 10
2022-02-16 02:00:18 - 3800145 - Shopify Q4 Earnings Preview: What to Expect
https://seekingalpha.com/news/3800145-shopify-q4-earnings-preview-what-to-expect

2022-02-15 16:20:21 - 3800395 - Upstart stock soars after Q4 earnings beat, strong guidance, stock buyback
https://seekingalpha.com/news/3800395-upstart-stock-soars-after-q4-earnings-beat-strong-guidance-stock-buyback

2022-02-15 11:31:14 - 3800203 - Greenview Capital takes stakes in Alibaba, Amazon
https://seekingalpha.com/news/3800203-greenview-capital-takes-stakes-in-alibaba-amazon

2022-02-15 16:38:11 - 3800438 - Roblox shares plunge as metaverse company misses Wall Street's expectations
https://seekingalpha.com/news/3800438-roblox-shares-plunge-as-metaverse-company-misses-wall-streets-expectations

2022-02-15 12:39:57 - 3800257 - Sunshine Biopharma announces pricing of $8M public offering, uplisting
https://seekingalpha.com/news/3800257-sunshine-biopharma-announces-pricing-of-8m-public-offering-uplisting

2022-02-15 14:06:05 - 3800296 - Cathie Wood’s ARKK a bubble? Let’s look at history
https://seekingalpha.com/news/3800296-is-cathie-woods-arkk-a-bubble-lets-look-at-history

2022-02-16 01:38:34 - 3800525 - Flex LNG Non-GAAP EPS of $1.18, revenue of $114.6M beats by $4.38M
https://seekingalpha.com/news/3800525-flex-lng-non-gaap-eps-of-118-revenue-of-1146m-beats-by-438m

2022-02-15 19:04:21 - 3800509 - ViacomCBS earnings call: A flood of content feeding transformation to Paramount
https://seekingalpha.com/news/3800509-viacomcbs-earnings-call-a-flood-of-content-feeding-transformation-to-paramount

2022-02-16 02:09:27 - 3800529 - Golden Ocean raises dividend by ~6% to $0.90/share
https://seekingalpha.com/news/3800529-golden-ocean-raises-dividend-by-6-to-090share

2022-02-15 17:35:20 - 3800169 - Matterport Q4 2021 Earnings Preview
https://seekingalpha.com/news/3800169-matterport-q4-2021-earnings-preview
```
---

---
title: getdd
description: OpenBB Terminal Function
---

# getdd

Print top stock's due diligence from other users. [Source: Reddit]

### Usage

```python
getdd [-l LIMIT] [-d DAYS] [-a]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | limit of posts to retrieve. | 5 | True | None |
| days | number of prior days to look for. | 3 | True | None |
| all | search through all flairs (apart from Yolo and Meme), otherwise we focus on specific flairs: DD, technical analysis, Catalyst, News, Advice, Chart | False | True | None |


---

## Examples

```python
2022 Feb 16, 10:18 (🦋) /stocks/ba/ $ getdd -d 50
2022-02-15 17:51:11 - $ATVI free money even if MSFT deal falls through.
https://old.reddit.com/r/wallstreetbets/comments/st8s1i/atvi_free_money_even_if_msft_deal_falls_through/

2022-02-10 05:10:31 - PTON: The safest investment you can make
https://old.reddit.com/r/stocks/comments/soycgc/pton_the_safest_investment_you_can_make/

2022-02-09 01:47:49 - Why only retards are selling the (near) bottom on $FB and are about to get metacucked 🙊
https://old.reddit.com/r/wallstreetbets/comments/so19al/why_only_retards_are_selling_the_near_bottom_on/)

2022-02-08 02:53:43 - If You Cannot Beat Them, Join Them - Congress Trading & Retail Traders
https://old.reddit.com/r/wallstreetbets/comments/sn90qs/if_you_cannot_beat_them_join_them_congress/

2022-02-03 20:01:06 - Thoughts on only buying large market cap stocks (Top 100, 100 billion market cap+, and significant index weighting)?
https://old.reddit.com/r/stocks/comments/sjsqhu/thoughts_on_only_buying_large_market_cap_stocks/
```
---

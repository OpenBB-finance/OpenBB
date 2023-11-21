---
title: fun
description: This page provides a comprehensive guide on how to use the python script
  'fun' to display various fundamental metrics from the Token Terminal. The metrics
  include market cap, timeline, category, etc. It also comes with specific command-line
  examples and parameter descriptions for better understanding.
keywords:
- fundamental metrics
- Token Terminal
- usage
- parameters
- python script
- examples
- market_cap
- Blockchain
- category
- metric
- timeline
- reverse
- limit
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/ov/fun - Reference | OpenBB Terminal Docs" />

Display fundamental metrics overview [Source: Token Terminal]

### Usage

```python
fun -m {twitter_followers,gmv_annualized,market_cap,take_rate,revenue,revenue_protocol,tvl,pe,pe_circulating,ps,ps_circulating} [-c {Asset Management,Blockchain,DeFi,Exchange,Gaming,Insurance,Interoperability,Lending,NFT,Other,Prediction Market,Stablecoin}] [-t {24h,7d,30d,90d,180d,365d}] [-r] [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| metric | Choose metric of interest | None | False | twitter_followers, gmv_annualized, market_cap, take_rate, revenue, revenue_protocol, tvl, pe, pe_circulating, ps, ps_circulating |
| category | Choose category of interest |  | True | Asset Management, Blockchain, DeFi, Exchange, Gaming, Insurance, Interoperability, Lending, NFT, Other, Prediction Market, Stablecoin |
| timeline | Choose timeline of interest | 24h | True | 24h, 7d, 30d, 90d, 180d, 365d |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| limit | Display N items | 10 | True | None |


---

## Examples

```python
2022 Aug 28, 20:02 (🦋) /crypto/ov/ $ fun -m market_cap -c Blockchain
```
---

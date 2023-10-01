---
title: fun
description: OpenBB Terminal Function
---

# fun

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

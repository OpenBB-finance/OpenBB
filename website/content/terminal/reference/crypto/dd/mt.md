---
title: mt
description: OpenBB Terminal Function
---

# mt

Display messari timeseries [Source: https://messari.io]

### Usage

```python
mt [--list] [-t TIMESERIES] [-i {5m,15m,30m,1h,1d,1w}] [-s START] [-end END] [--include-paid] [-q QUERY [QUERY ...]]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| list | Flag to show available timeseries | False | True | None |
| timeseries | Messari timeseries id |  | True | mcap.circ, sply.liquid, txn.fee.avg, sply.total.iss, exch.flow.out.usd, daily.vol, reddit.active.users, mcap.out, txn.cnt, txn.tsfr.val.adj, exch.sply.ntv, txn.tfr.val.ntv, txn.tfr.val.adj.ntv, daily.shp, sply.out, txn.tfr.avg.ntv, act.addr.cnt, iss.rate, mcap.dom, blk.size.byte, new.iss.ntv, diff.avg, txn.vol, exch.sply.usd, txn.tfr.val.med, exch.flow.out.ntv.incl, fees.ntv, twitter.followers, exch.flow.in.usd, min.rev.usd, new.iss.usd, min.rev.ntv, hashrate, txn.tsfr.val.avg, txn.tfr.erc721.cnt, exch.flow.out.usd.incl, nvt.adj.90d.ma, cg.sply.circ, txn.fee.med, exch.flow.in.usd.incl, reddit.subscribers, sply.circ, txn.tfr.val.med.ntv, blk.size.bytes.avg, exch.flow.in.ntv, txn.tsfr.cnt, exch.flow.in.ntv.incl, real.vol, txn.tfr.erc20.cnt, blk.cnt, fees, sply.total.iss.ntv, nvt.adj, txn.fee.avg.ntv, txn.fee.med.ntv, telegram.users, mcap.realized, price, exch.flow.out.ntv |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

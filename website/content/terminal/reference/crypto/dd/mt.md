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
| timeseries | Messari timeseries id |  | True | exch.flow.out.ntv.incl, new.iss.ntv, sply.liquid, txn.fee.avg.ntv, blk.size.byte, txn.fee.avg, min.rev.ntv, txn.cnt, txn.tsfr.val.avg, sply.out, daily.shp, exch.sply.usd, exch.flow.in.usd, new.iss.usd, txn.fee.med.ntv, exch.flow.out.usd.incl, reddit.active.users, txn.tfr.val.adj.ntv, iss.rate, fees, txn.tfr.erc721.cnt, txn.tfr.avg.ntv, mcap.circ, exch.flow.in.usd.incl, diff.avg, txn.tfr.erc20.cnt, sply.circ, sply.total.iss.ntv, txn.tfr.val.med, exch.flow.in.ntv, txn.tsfr.cnt, txn.vol, txn.tsfr.val.adj, telegram.users, reddit.subscribers, hashrate, blk.cnt, sply.total.iss, fees.ntv, min.rev.usd, twitter.followers, act.addr.cnt, mcap.dom, blk.size.bytes.avg, exch.sply.ntv, mcap.out, txn.fee.med, price, cg.sply.circ, daily.vol, exch.flow.in.ntv.incl, exch.flow.out.ntv, mcap.realized, exch.flow.out.usd, nvt.adj.90d.ma, txn.tfr.val.ntv, real.vol, nvt.adj, txn.tfr.val.med.ntv |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

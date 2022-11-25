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
| timeseries | Messari timeseries id |  | True | txn.tsfr.val.avg, daily.shp, txn.tfr.erc721.cnt, hashrate, txn.fee.med.ntv, blk.cnt, exch.flow.in.ntv.incl, blk.size.bytes.avg, real.vol, blk.size.byte, cg.sply.circ, exch.flow.in.ntv, min.rev.usd, nvt.adj.90d.ma, sply.liquid, txn.tsfr.cnt, txn.vol, exch.flow.in.usd.incl, exch.flow.out.usd.incl, exch.flow.out.usd, mcap.dom, txn.fee.avg, fees, txn.fee.med, act.addr.cnt, sply.total.iss.ntv, exch.flow.out.ntv.incl, fees.ntv, nvt.adj, sply.out, mcap.realized, sply.total.iss, exch.flow.out.ntv, new.iss.usd, txn.tfr.val.ntv, txn.tfr.val.adj.ntv, sply.circ, twitter.followers, min.rev.ntv, diff.avg, exch.sply.usd, new.iss.ntv, txn.fee.avg.ntv, price, txn.tsfr.val.adj, txn.tfr.erc20.cnt, txn.tfr.val.med, iss.rate, txn.tfr.avg.ntv, txn.cnt, txn.tfr.val.med.ntv, reddit.active.users, reddit.subscribers, telegram.users, exch.sply.ntv, mcap.out, exch.flow.in.usd, mcap.circ, daily.vol |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-25 | True | None |
| end | End date. Default: Today | 2022-11-25 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

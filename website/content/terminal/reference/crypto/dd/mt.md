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
| timeseries | Messari timeseries id |  | True | txn.tfr.val.med.ntv, blk.size.byte, sply.circ, sply.total.iss, diff.avg, txn.tfr.avg.ntv, mcap.realized, mcap.dom, daily.vol, mcap.circ, txn.fee.avg, reddit.subscribers, twitter.followers, hashrate, sply.total.iss.ntv, exch.sply.ntv, exch.flow.out.usd, txn.fee.med, blk.size.bytes.avg, fees.ntv, exch.flow.in.usd.incl, exch.flow.in.usd, txn.fee.avg.ntv, exch.flow.out.ntv.incl, nvt.adj.90d.ma, sply.out, fees, txn.tfr.erc20.cnt, blk.cnt, reddit.active.users, telegram.users, new.iss.ntv, act.addr.cnt, exch.sply.usd, txn.tsfr.cnt, txn.vol, cg.sply.circ, sply.liquid, txn.tfr.val.ntv, txn.tsfr.val.avg, txn.cnt, txn.tsfr.val.adj, exch.flow.out.ntv, txn.fee.med.ntv, min.rev.ntv, new.iss.usd, exch.flow.in.ntv.incl, nvt.adj, daily.shp, exch.flow.in.ntv, exch.flow.out.usd.incl, min.rev.usd, txn.tfr.val.med, txn.tfr.erc721.cnt, price, mcap.out, real.vol, iss.rate, txn.tfr.val.adj.ntv |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-25 | True | None |
| end | End date. Default: Today | 2022-11-25 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

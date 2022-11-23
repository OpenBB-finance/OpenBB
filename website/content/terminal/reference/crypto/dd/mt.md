---
title: mt
description: OpenBB Terminal Function
---

# mt

Display messari timeseries [Source: https://messari.io]

### Usage

```python
usage: mt [--list] [-t TIMESERIES] [-i {5m,15m,30m,1h,1d,1w}] [-s START] [-end END] [--include-paid] [-q QUERY [QUERY ...]]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| list | Flag to show available timeseries | False | True | None |
| timeseries | Messari timeseries id |  | True | cg.sply.circ, txn.tsfr.cnt, exch.flow.in.usd.incl, sply.circ, fees, act.addr.cnt, sply.total.iss, exch.flow.out.usd, telegram.users, txn.tfr.val.adj.ntv, exch.sply.usd, nvt.adj, exch.flow.in.ntv.incl, txn.tsfr.val.adj, min.rev.ntv, new.iss.ntv, mcap.circ, iss.rate, sply.total.iss.ntv, blk.size.bytes.avg, txn.cnt, daily.vol, sply.liquid, exch.flow.in.usd, mcap.dom, txn.tsfr.val.avg, real.vol, txn.vol, reddit.subscribers, price, mcap.realized, new.iss.usd, daily.shp, sply.out, exch.sply.ntv, txn.tfr.erc721.cnt, exch.flow.out.usd.incl, txn.fee.med, txn.fee.avg.ntv, txn.fee.avg, blk.size.byte, exch.flow.in.ntv, nvt.adj.90d.ma, hashrate, exch.flow.out.ntv, fees.ntv, twitter.followers, txn.tfr.val.med, txn.fee.med.ntv, txn.tfr.val.ntv, txn.tfr.erc20.cnt, txn.tfr.val.med.ntv, blk.cnt, diff.avg, min.rev.usd, reddit.active.users, mcap.out, txn.tfr.avg.ntv, exch.flow.out.ntv.incl |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-23 | True | None |
| end | End date. Default: Today | 2022-11-23 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

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
| timeseries | Messari timeseries id |  | True | txn.vol, txn.tsfr.val.avg, txn.tsfr.cnt, txn.tfr.val.med.ntv, sply.liquid, txn.fee.med, nvt.adj.90d.ma, txn.tfr.val.med, sply.circ, txn.fee.med.ntv, fees.ntv, exch.flow.in.ntv, act.addr.cnt, twitter.followers, exch.sply.usd, exch.flow.in.ntv.incl, mcap.dom, blk.size.bytes.avg, reddit.subscribers, sply.total.iss.ntv, txn.fee.avg.ntv, exch.flow.out.usd, new.iss.usd, mcap.out, hashrate, txn.tfr.val.adj.ntv, exch.flow.out.ntv.incl, new.iss.ntv, exch.flow.out.ntv, diff.avg, txn.tfr.erc721.cnt, telegram.users, real.vol, price, exch.sply.ntv, txn.fee.avg, txn.tfr.val.ntv, reddit.active.users, blk.size.byte, fees, exch.flow.in.usd, exch.flow.in.usd.incl, sply.out, daily.vol, cg.sply.circ, min.rev.ntv, blk.cnt, min.rev.usd, nvt.adj, txn.tfr.avg.ntv, txn.tsfr.val.adj, exch.flow.out.usd.incl, mcap.realized, iss.rate, txn.tfr.erc20.cnt, mcap.circ, daily.shp, sply.total.iss, txn.cnt |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

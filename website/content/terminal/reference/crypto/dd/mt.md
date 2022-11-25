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
| timeseries | Messari timeseries id |  | True | txn.tfr.avg.ntv, txn.tfr.val.med, daily.shp, reddit.subscribers, nvt.adj.90d.ma, min.rev.ntv, txn.tfr.val.med.ntv, min.rev.usd, new.iss.usd, blk.size.byte, exch.flow.in.ntv, exch.flow.in.usd, exch.flow.out.ntv.incl, new.iss.ntv, sply.total.iss.ntv, mcap.realized, daily.vol, sply.liquid, sply.total.iss, reddit.active.users, hashrate, sply.out, exch.flow.out.ntv, mcap.dom, exch.sply.usd, cg.sply.circ, fees.ntv, exch.flow.in.usd.incl, blk.size.bytes.avg, txn.cnt, mcap.out, price, mcap.circ, txn.tfr.val.ntv, blk.cnt, sply.circ, real.vol, txn.fee.avg, txn.vol, txn.fee.med, diff.avg, fees, txn.tsfr.val.adj, nvt.adj, exch.flow.in.ntv.incl, iss.rate, exch.flow.out.usd, txn.tsfr.val.avg, act.addr.cnt, txn.fee.avg.ntv, twitter.followers, exch.flow.out.usd.incl, txn.fee.med.ntv, txn.tsfr.cnt, telegram.users, txn.tfr.val.adj.ntv, exch.sply.ntv, txn.tfr.erc20.cnt, txn.tfr.erc721.cnt |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-25 | True | None |
| end | End date. Default: Today | 2022-11-25 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

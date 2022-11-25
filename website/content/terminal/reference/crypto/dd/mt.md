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
| timeseries | Messari timeseries id |  | True | act.addr.cnt, fees.ntv, mcap.out, txn.vol, twitter.followers, txn.tsfr.val.adj, txn.tsfr.val.avg, txn.fee.med.ntv, txn.tfr.erc20.cnt, new.iss.ntv, txn.tfr.val.med, txn.tfr.erc721.cnt, txn.cnt, real.vol, mcap.circ, mcap.realized, fees, sply.circ, min.rev.ntv, blk.cnt, exch.flow.out.usd, sply.out, txn.tfr.val.med.ntv, exch.flow.in.usd, nvt.adj.90d.ma, daily.shp, reddit.subscribers, telegram.users, txn.tfr.avg.ntv, blk.size.bytes.avg, hashrate, txn.tsfr.cnt, cg.sply.circ, exch.flow.in.ntv.incl, txn.fee.avg.ntv, exch.flow.in.usd.incl, sply.total.iss, txn.fee.avg, exch.sply.usd, diff.avg, sply.total.iss.ntv, min.rev.usd, nvt.adj, txn.tfr.val.adj.ntv, exch.sply.ntv, exch.flow.out.ntv.incl, txn.tfr.val.ntv, exch.flow.out.ntv, price, mcap.dom, sply.liquid, reddit.active.users, blk.size.byte, new.iss.usd, exch.flow.out.usd.incl, exch.flow.in.ntv, iss.rate, daily.vol, txn.fee.med |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-25 | True | None |
| end | End date. Default: Today | 2022-11-25 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

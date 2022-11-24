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
| timeseries | Messari timeseries id |  | True | hashrate, sply.total.iss, blk.cnt, fees.ntv, min.rev.usd, twitter.followers, act.addr.cnt, blk.size.bytes.avg, exch.sply.ntv, mcap.out, mcap.dom, txn.fee.med, price, cg.sply.circ, exch.flow.in.ntv.incl, exch.flow.out.ntv, mcap.realized, daily.vol, exch.flow.out.usd, nvt.adj.90d.ma, txn.tfr.val.ntv, nvt.adj, real.vol, txn.tfr.val.med.ntv, exch.flow.out.ntv.incl, new.iss.ntv, sply.liquid, txn.fee.avg, txn.fee.avg.ntv, blk.size.byte, min.rev.ntv, txn.tsfr.val.avg, txn.cnt, sply.out, daily.shp, exch.sply.usd, new.iss.usd, exch.flow.in.usd, txn.fee.med.ntv, exch.flow.out.usd.incl, txn.tfr.val.adj.ntv, reddit.active.users, iss.rate, fees, txn.tfr.avg.ntv, txn.tfr.erc721.cnt, exch.flow.in.usd.incl, mcap.circ, txn.tfr.erc20.cnt, diff.avg, sply.total.iss.ntv, txn.tfr.val.med, sply.circ, txn.tsfr.cnt, txn.vol, exch.flow.in.ntv, txn.tsfr.val.adj, telegram.users, reddit.subscribers |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

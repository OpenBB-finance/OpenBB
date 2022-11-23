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
| timeseries | Messari timeseries id |  | True | new.iss.ntv, act.addr.cnt, exch.flow.out.ntv, mcap.out, daily.shp, txn.cnt, mcap.dom, sply.total.iss.ntv, txn.vol, exch.sply.ntv, mcap.circ, reddit.active.users, fees, txn.tsfr.val.avg, txn.tfr.val.ntv, txn.fee.avg, daily.vol, reddit.subscribers, exch.sply.usd, exch.flow.in.usd.incl, blk.size.bytes.avg, min.rev.ntv, txn.fee.med, exch.flow.in.ntv, iss.rate, sply.total.iss, blk.size.byte, fees.ntv, new.iss.usd, txn.tsfr.cnt, nvt.adj.90d.ma, exch.flow.out.ntv.incl, real.vol, txn.tfr.erc20.cnt, txn.tsfr.val.adj, txn.tfr.avg.ntv, sply.circ, sply.liquid, min.rev.usd, txn.fee.avg.ntv, exch.flow.out.usd, mcap.realized, diff.avg, twitter.followers, exch.flow.in.ntv.incl, txn.tfr.erc721.cnt, txn.tfr.val.med.ntv, txn.tfr.val.adj.ntv, exch.flow.out.usd.incl, blk.cnt, nvt.adj, hashrate, txn.tfr.val.med, price, txn.fee.med.ntv, telegram.users, sply.out, exch.flow.in.usd, cg.sply.circ |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-23 | True | None |
| end | End date. Default: Today | 2022-11-23 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

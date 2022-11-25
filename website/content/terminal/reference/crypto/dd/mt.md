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
| timeseries | Messari timeseries id |  | True | exch.sply.usd, cg.sply.circ, exch.flow.in.usd.incl, txn.fee.avg.ntv, new.iss.usd, txn.tfr.val.adj.ntv, exch.flow.out.ntv, new.iss.ntv, txn.vol, min.rev.ntv, txn.fee.med.ntv, daily.vol, txn.fee.avg, blk.size.byte, blk.cnt, txn.tfr.val.ntv, exch.flow.out.usd.incl, txn.cnt, txn.fee.med, txn.tfr.avg.ntv, daily.shp, exch.flow.out.ntv.incl, mcap.realized, txn.tsfr.cnt, txn.tfr.erc721.cnt, exch.sply.ntv, mcap.dom, mcap.circ, blk.size.bytes.avg, mcap.out, min.rev.usd, act.addr.cnt, sply.circ, sply.liquid, fees.ntv, exch.flow.in.usd, iss.rate, hashrate, nvt.adj, txn.tsfr.val.avg, reddit.active.users, txn.tfr.val.med, txn.tsfr.val.adj, exch.flow.out.usd, price, fees, sply.total.iss.ntv, exch.flow.in.ntv, nvt.adj.90d.ma, exch.flow.in.ntv.incl, twitter.followers, reddit.subscribers, sply.out, txn.tfr.erc20.cnt, diff.avg, txn.tfr.val.med.ntv, telegram.users, sply.total.iss, real.vol |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-25 | True | None |
| end | End date. Default: Today | 2022-11-25 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

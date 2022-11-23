---
title: mt
description: OpenBB Terminal Function
---

# mt

Display messari timeseries [Source: https://messari.io]

### Usage

```python
usage: mt [--list] [-t TIMESERIES] [-i {5m,15m,30m,1h,1d,1w}] [-s START]
          [-end END] [--include-paid] [-q QUERY [QUERY ...]]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| list | Flag to show available timeseries | False | True | None |
| timeseries | Messari timeseries id |  | True | twitter.followers, min.rev.usd, exch.flow.out.ntv, real.vol, blk.size.bytes.avg, txn.tfr.val.med.ntv, fees.ntv, nvt.adj.90d.ma, price, exch.flow.in.ntv, txn.fee.avg.ntv, exch.flow.in.usd, sply.out, new.iss.usd, sply.circ, sply.total.iss.ntv, txn.fee.avg, txn.tfr.val.adj.ntv, exch.sply.ntv, mcap.dom, txn.tsfr.val.adj, blk.cnt, txn.tfr.erc20.cnt, txn.tfr.erc721.cnt, txn.tfr.val.ntv, daily.vol, txn.fee.med, mcap.realized, txn.fee.med.ntv, sply.liquid, txn.cnt, exch.flow.in.ntv.incl, exch.flow.out.ntv.incl, sply.total.iss, mcap.circ, txn.tsfr.cnt, act.addr.cnt, blk.size.byte, new.iss.ntv, reddit.active.users, exch.flow.in.usd.incl, nvt.adj, txn.tfr.avg.ntv, telegram.users, txn.tsfr.val.avg, hashrate, exch.sply.usd, mcap.out, daily.shp, exch.flow.out.usd, iss.rate, exch.flow.out.usd.incl, reddit.subscribers, diff.avg, fees, txn.vol, cg.sply.circ, txn.tfr.val.med, min.rev.ntv |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-23 | True | None |
| end | End date. Default: Today | 2022-11-23 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

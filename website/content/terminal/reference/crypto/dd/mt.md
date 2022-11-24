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
| timeseries | Messari timeseries id |  | True | txn.tfr.erc20.cnt, exch.flow.out.ntv.incl, txn.cnt, exch.flow.out.usd.incl, txn.vol, fees, fees.ntv, txn.fee.avg, txn.tsfr.val.avg, cg.sply.circ, txn.fee.med, min.rev.ntv, exch.flow.in.usd, txn.fee.avg.ntv, iss.rate, mcap.realized, sply.circ, real.vol, txn.tfr.avg.ntv, price, txn.tsfr.cnt, sply.total.iss, txn.tfr.erc721.cnt, blk.size.byte, txn.fee.med.ntv, txn.tfr.val.ntv, exch.sply.ntv, exch.flow.in.ntv.incl, diff.avg, blk.size.bytes.avg, act.addr.cnt, exch.sply.usd, new.iss.usd, min.rev.usd, sply.liquid, daily.vol, daily.shp, txn.tsfr.val.adj, hashrate, exch.flow.in.ntv, sply.total.iss.ntv, mcap.out, reddit.subscribers, txn.tfr.val.med.ntv, sply.out, telegram.users, exch.flow.out.ntv, exch.flow.in.usd.incl, blk.cnt, new.iss.ntv, nvt.adj, txn.tfr.val.adj.ntv, exch.flow.out.usd, nvt.adj.90d.ma, twitter.followers, mcap.circ, txn.tfr.val.med, mcap.dom, reddit.active.users |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

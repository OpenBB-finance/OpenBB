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
| timeseries | Messari timeseries id |  | True | txn.tfr.val.ntv, txn.tfr.val.adj.ntv, new.iss.usd, txn.fee.med.ntv, mcap.realized, mcap.dom, blk.size.byte, blk.size.bytes.avg, hashrate, exch.sply.ntv, diff.avg, min.rev.ntv, txn.vol, txn.tsfr.val.avg, act.addr.cnt, txn.tfr.avg.ntv, blk.cnt, telegram.users, exch.flow.in.ntv, exch.flow.out.usd, daily.vol, exch.flow.in.usd.incl, exch.flow.out.ntv.incl, mcap.circ, reddit.active.users, txn.cnt, sply.liquid, exch.flow.in.ntv.incl, fees, exch.sply.usd, txn.fee.avg, exch.flow.in.usd, txn.fee.avg.ntv, exch.flow.out.ntv, mcap.out, txn.tfr.erc721.cnt, txn.tsfr.val.adj, txn.tfr.val.med, nvt.adj.90d.ma, nvt.adj, daily.shp, sply.total.iss, price, exch.flow.out.usd.incl, cg.sply.circ, min.rev.usd, new.iss.ntv, sply.total.iss.ntv, txn.tfr.erc20.cnt, txn.fee.med, real.vol, reddit.subscribers, txn.tsfr.cnt, txn.tfr.val.med.ntv, fees.ntv, sply.circ, twitter.followers, sply.out, iss.rate |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

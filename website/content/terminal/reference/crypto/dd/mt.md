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
| timeseries | Messari timeseries id |  | True | mcap.dom, txn.tfr.avg.ntv, exch.sply.ntv, nvt.adj.90d.ma, txn.tsfr.val.adj, cg.sply.circ, new.iss.ntv, blk.cnt, blk.size.byte, txn.vol, act.addr.cnt, sply.total.iss, sply.out, new.iss.usd, telegram.users, exch.flow.in.ntv.incl, exch.flow.out.ntv.incl, exch.flow.in.ntv, exch.flow.in.usd, exch.flow.out.ntv, iss.rate, txn.fee.med, txn.fee.avg.ntv, txn.tsfr.cnt, price, exch.flow.out.usd.incl, exch.flow.out.usd, txn.tfr.erc20.cnt, txn.tsfr.val.avg, txn.tfr.val.med, txn.cnt, sply.liquid, nvt.adj, txn.tfr.val.ntv, sply.total.iss.ntv, sply.circ, mcap.realized, txn.tfr.erc721.cnt, hashrate, min.rev.ntv, real.vol, txn.fee.avg, txn.tfr.val.med.ntv, fees, mcap.out, blk.size.bytes.avg, exch.sply.usd, reddit.subscribers, twitter.followers, mcap.circ, txn.fee.med.ntv, txn.tfr.val.adj.ntv, reddit.active.users, fees.ntv, daily.vol, exch.flow.in.usd.incl, daily.shp, diff.avg, min.rev.usd |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

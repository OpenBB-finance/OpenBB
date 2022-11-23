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
| timeseries | Messari timeseries id |  | True | mcap.realized, txn.fee.avg.ntv, mcap.out, txn.tsfr.val.avg, sply.total.iss.ntv, txn.vol, real.vol, exch.flow.in.usd, txn.fee.avg, exch.flow.in.ntv.incl, exch.flow.out.ntv.incl, reddit.active.users, sply.liquid, mcap.circ, txn.tsfr.cnt, hashrate, fees, iss.rate, txn.tfr.erc20.cnt, exch.flow.in.ntv, txn.fee.med, new.iss.ntv, mcap.dom, txn.tfr.val.med.ntv, twitter.followers, reddit.subscribers, blk.size.byte, telegram.users, sply.circ, sply.out, daily.shp, sply.total.iss, min.rev.usd, cg.sply.circ, act.addr.cnt, exch.flow.in.usd.incl, exch.sply.ntv, exch.flow.out.usd, txn.tfr.val.med, new.iss.usd, price, exch.sply.usd, exch.flow.out.usd.incl, txn.tfr.val.ntv, blk.cnt, txn.cnt, fees.ntv, txn.fee.med.ntv, exch.flow.out.ntv, daily.vol, diff.avg, txn.tfr.avg.ntv, txn.tsfr.val.adj, nvt.adj, blk.size.bytes.avg, txn.tfr.erc721.cnt, nvt.adj.90d.ma, min.rev.ntv, txn.tfr.val.adj.ntv |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-23 | True | None |
| end | End date. Default: Today | 2022-11-23 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

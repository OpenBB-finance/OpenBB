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
| timeseries | Messari timeseries id |  | True | txn.fee.med, txn.tsfr.val.avg, mcap.out, reddit.subscribers, exch.flow.in.ntv.incl, telegram.users, txn.vol, min.rev.usd, real.vol, exch.flow.out.usd.incl, min.rev.ntv, nvt.adj, sply.circ, reddit.active.users, act.addr.cnt, txn.tfr.avg.ntv, txn.cnt, twitter.followers, blk.size.bytes.avg, exch.flow.out.usd, txn.fee.med.ntv, mcap.circ, txn.tsfr.val.adj, price, txn.tfr.val.ntv, exch.flow.in.usd, txn.tfr.erc721.cnt, mcap.realized, exch.flow.in.ntv, exch.sply.usd, daily.vol, txn.tfr.val.adj.ntv, mcap.dom, txn.fee.avg, txn.tfr.val.med.ntv, fees.ntv, fees, diff.avg, sply.out, sply.total.iss, sply.total.iss.ntv, nvt.adj.90d.ma, exch.flow.out.ntv.incl, exch.flow.out.ntv, blk.cnt, iss.rate, txn.tfr.erc20.cnt, sply.liquid, blk.size.byte, new.iss.usd, exch.sply.ntv, new.iss.ntv, hashrate, cg.sply.circ, daily.shp, txn.fee.avg.ntv, txn.tfr.val.med, exch.flow.in.usd.incl, txn.tsfr.cnt |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

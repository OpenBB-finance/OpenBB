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
| timeseries | Messari timeseries id |  | True | hashrate, sply.out, txn.fee.med, exch.sply.usd, min.rev.ntv, txn.tfr.erc721.cnt, mcap.realized, exch.sply.ntv, txn.tsfr.val.adj, fees, txn.tsfr.val.avg, txn.fee.med.ntv, reddit.active.users, diff.avg, exch.flow.out.usd, txn.tfr.erc20.cnt, mcap.out, mcap.dom, sply.liquid, txn.fee.avg.ntv, txn.vol, real.vol, exch.flow.out.usd.incl, txn.tfr.val.ntv, telegram.users, min.rev.usd, fees.ntv, txn.tfr.val.adj.ntv, txn.tfr.val.med.ntv, exch.flow.in.usd, txn.tfr.val.med, new.iss.ntv, txn.cnt, reddit.subscribers, new.iss.usd, daily.shp, txn.tsfr.cnt, exch.flow.out.ntv.incl, txn.tfr.avg.ntv, blk.size.byte, exch.flow.in.usd.incl, exch.flow.out.ntv, sply.total.iss, mcap.circ, daily.vol, blk.cnt, nvt.adj.90d.ma, blk.size.bytes.avg, exch.flow.in.ntv.incl, iss.rate, nvt.adj, price, txn.fee.avg, twitter.followers, sply.circ, exch.flow.in.ntv, sply.total.iss.ntv, cg.sply.circ, act.addr.cnt |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-23 | True | None |
| end | End date. Default: Today | 2022-11-23 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

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
| timeseries | Messari timeseries id |  | True | mcap.realized, fees, iss.rate, reddit.active.users, nvt.adj.90d.ma, txn.tfr.val.med.ntv, daily.vol, exch.flow.in.ntv, mcap.dom, blk.cnt, txn.vol, sply.total.iss, txn.tfr.avg.ntv, txn.tsfr.val.adj, exch.flow.out.usd, nvt.adj, txn.tsfr.val.avg, txn.fee.med.ntv, fees.ntv, blk.size.byte, txn.tfr.val.ntv, txn.tfr.val.med, mcap.circ, sply.liquid, exch.flow.in.usd, sply.out, exch.flow.out.ntv.incl, exch.flow.in.ntv.incl, exch.sply.usd, exch.flow.out.usd.incl, txn.cnt, exch.flow.in.usd.incl, daily.shp, txn.tfr.val.adj.ntv, price, hashrate, exch.flow.out.ntv, real.vol, exch.sply.ntv, txn.fee.avg, txn.tfr.erc721.cnt, twitter.followers, telegram.users, reddit.subscribers, cg.sply.circ, blk.size.bytes.avg, txn.fee.avg.ntv, txn.fee.med, txn.tsfr.cnt, sply.circ, mcap.out, diff.avg, act.addr.cnt, min.rev.ntv, new.iss.ntv, min.rev.usd, new.iss.usd, sply.total.iss.ntv, txn.tfr.erc20.cnt |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-25 | True | None |
| end | End date. Default: Today | 2022-11-25 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

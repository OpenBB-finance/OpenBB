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
| timeseries | Messari timeseries id |  | True | txn.vol, txn.tsfr.val.avg, txn.fee.med, exch.flow.out.ntv, txn.tfr.avg.ntv, reddit.active.users, exch.flow.in.ntv.incl, exch.flow.in.usd.incl, fees, mcap.dom, hashrate, txn.cnt, txn.tfr.val.med.ntv, price, txn.tfr.erc721.cnt, txn.tfr.val.adj.ntv, min.rev.ntv, min.rev.usd, fees.ntv, txn.tfr.val.ntv, exch.flow.in.usd, new.iss.usd, txn.tsfr.val.adj, daily.vol, nvt.adj, txn.fee.med.ntv, sply.out, mcap.circ, exch.flow.out.usd, twitter.followers, txn.tfr.erc20.cnt, nvt.adj.90d.ma, mcap.realized, txn.tfr.val.med, exch.sply.usd, sply.liquid, sply.total.iss.ntv, exch.flow.in.ntv, daily.shp, exch.sply.ntv, sply.circ, blk.cnt, real.vol, txn.fee.avg.ntv, blk.size.byte, txn.tsfr.cnt, mcap.out, blk.size.bytes.avg, txn.fee.avg, diff.avg, reddit.subscribers, exch.flow.out.ntv.incl, exch.flow.out.usd.incl, act.addr.cnt, telegram.users, new.iss.ntv, iss.rate, sply.total.iss, cg.sply.circ |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-25 | True | None |
| end | End date. Default: Today | 2022-11-25 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

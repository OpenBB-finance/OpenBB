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
| timeseries | Messari timeseries id |  | True | sply.total.iss, reddit.active.users, sply.total.iss.ntv, min.rev.usd, reddit.subscribers, nvt.adj, telegram.users, mcap.out, sply.circ, txn.tfr.val.adj.ntv, cg.sply.circ, fees, txn.tfr.val.ntv, txn.tsfr.cnt, exch.flow.in.usd.incl, fees.ntv, blk.size.byte, txn.tfr.erc20.cnt, diff.avg, txn.tsfr.val.adj, mcap.realized, exch.sply.usd, txn.tsfr.val.avg, exch.flow.in.ntv, sply.out, exch.sply.ntv, txn.fee.avg, txn.tfr.val.med.ntv, exch.flow.out.ntv.incl, mcap.circ, sply.liquid, iss.rate, txn.vol, min.rev.ntv, daily.shp, twitter.followers, txn.tfr.erc721.cnt, exch.flow.in.ntv.incl, exch.flow.in.usd, new.iss.ntv, txn.fee.med, txn.tfr.val.med, new.iss.usd, txn.tfr.avg.ntv, daily.vol, real.vol, hashrate, act.addr.cnt, nvt.adj.90d.ma, blk.cnt, exch.flow.out.usd.incl, exch.flow.out.ntv, blk.size.bytes.avg, txn.cnt, txn.fee.avg.ntv, txn.fee.med.ntv, price, mcap.dom, exch.flow.out.usd |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-25 | True | None |
| end | End date. Default: Today | 2022-11-25 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

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
| timeseries | Messari timeseries id |  | True | hashrate, txn.tfr.val.med.ntv, blk.size.bytes.avg, sply.total.iss.ntv, exch.flow.in.usd.incl, mcap.circ, daily.vol, sply.total.iss, reddit.subscribers, txn.tsfr.val.avg, iss.rate, blk.size.byte, min.rev.ntv, txn.fee.avg, sply.liquid, exch.flow.out.ntv.incl, exch.flow.out.usd.incl, cg.sply.circ, txn.tsfr.val.adj, exch.flow.out.ntv, min.rev.usd, sply.circ, mcap.dom, reddit.active.users, txn.tsfr.cnt, daily.shp, exch.sply.ntv, mcap.out, txn.fee.med, real.vol, blk.cnt, exch.flow.out.usd, sply.out, new.iss.usd, txn.tfr.val.ntv, twitter.followers, txn.tfr.val.med, telegram.users, new.iss.ntv, txn.vol, exch.flow.in.usd, txn.tfr.val.adj.ntv, txn.tfr.avg.ntv, exch.flow.in.ntv, nvt.adj.90d.ma, txn.tfr.erc20.cnt, txn.tfr.erc721.cnt, act.addr.cnt, txn.fee.med.ntv, price, txn.cnt, fees, mcap.realized, diff.avg, txn.fee.avg.ntv, exch.flow.in.ntv.incl, exch.sply.usd, fees.ntv, nvt.adj |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-25 | True | None |
| end | End date. Default: Today | 2022-11-25 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

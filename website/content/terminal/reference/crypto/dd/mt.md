---
title: mt
description: OpenBB Terminal Function
---

# mt

Display messari timeseries [Source: https://messari.io]

### Usage

```python
usage: mt [--list] [-t TIMESERIES] [-i {5m,15m,30m,1h,1d,1w}] [-s START] [-end END] [--include-paid] [-q QUERY [QUERY ...]]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| list | Flag to show available timeseries | False | True | None |
| timeseries | Messari timeseries id |  | True | sply.out, exch.flow.out.usd.incl, txn.tfr.erc20.cnt, fees, diff.avg, blk.cnt, sply.total.iss.ntv, txn.tsfr.val.avg, price, fees.ntv, exch.flow.out.usd, new.iss.usd, sply.total.iss, real.vol, act.addr.cnt, txn.tsfr.val.adj, mcap.dom, txn.tfr.val.ntv, mcap.out, nvt.adj.90d.ma, reddit.active.users, txn.vol, reddit.subscribers, txn.fee.med.ntv, txn.fee.avg.ntv, daily.vol, blk.size.byte, exch.sply.ntv, exch.flow.in.ntv, hashrate, cg.sply.circ, exch.flow.out.ntv, txn.cnt, mcap.realized, daily.shp, nvt.adj, txn.tfr.val.med.ntv, txn.tfr.val.med, txn.tfr.val.adj.ntv, min.rev.ntv, txn.tfr.avg.ntv, exch.flow.in.usd.incl, telegram.users, txn.tfr.erc721.cnt, exch.flow.in.ntv.incl, txn.fee.med, iss.rate, txn.tsfr.cnt, sply.circ, mcap.circ, exch.sply.usd, exch.flow.in.usd, blk.size.bytes.avg, new.iss.ntv, exch.flow.out.ntv.incl, sply.liquid, twitter.followers, min.rev.usd, txn.fee.avg |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-23 | True | None |
| end | End date. Default: Today | 2022-11-23 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

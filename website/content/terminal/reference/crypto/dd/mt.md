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
| timeseries | Messari timeseries id |  | True | exch.sply.ntv, act.addr.cnt, exch.flow.in.ntv, txn.fee.med.ntv, fees, sply.liquid, hashrate, exch.flow.in.ntv.incl, txn.tsfr.cnt, nvt.adj.90d.ma, sply.out, cg.sply.circ, txn.tfr.val.adj.ntv, reddit.subscribers, new.iss.ntv, txn.tfr.erc20.cnt, telegram.users, blk.size.bytes.avg, txn.tfr.val.med.ntv, new.iss.usd, txn.vol, twitter.followers, exch.flow.in.usd.incl, sply.total.iss, txn.tfr.val.ntv, daily.shp, txn.tsfr.val.adj, exch.flow.out.usd.incl, exch.flow.in.usd, diff.avg, mcap.dom, exch.flow.out.ntv.incl, exch.flow.out.ntv, txn.fee.med, sply.circ, nvt.adj, txn.cnt, txn.tfr.avg.ntv, txn.fee.avg, fees.ntv, blk.size.byte, txn.tsfr.val.avg, mcap.circ, exch.sply.usd, iss.rate, exch.flow.out.usd, txn.tfr.erc721.cnt, txn.tfr.val.med, real.vol, blk.cnt, mcap.realized, txn.fee.avg.ntv, reddit.active.users, min.rev.ntv, min.rev.usd, price, daily.vol, sply.total.iss.ntv, mcap.out |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

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
| timeseries | Messari timeseries id |  | True | exch.flow.out.ntv.incl, txn.fee.med.ntv, daily.vol, twitter.followers, txn.fee.med, txn.vol, blk.cnt, txn.tsfr.val.avg, price, iss.rate, mcap.dom, blk.size.bytes.avg, txn.tfr.val.adj.ntv, blk.size.byte, nvt.adj.90d.ma, fees, exch.flow.in.ntv, exch.sply.usd, exch.flow.in.usd, nvt.adj, txn.tfr.avg.ntv, txn.tsfr.cnt, cg.sply.circ, diff.avg, sply.total.iss, new.iss.usd, hashrate, act.addr.cnt, sply.total.iss.ntv, txn.fee.avg.ntv, sply.circ, txn.tsfr.val.adj, exch.flow.out.ntv, txn.fee.avg, new.iss.ntv, txn.tfr.val.ntv, txn.tfr.erc20.cnt, reddit.subscribers, fees.ntv, daily.shp, exch.flow.in.usd.incl, sply.liquid, exch.flow.in.ntv.incl, mcap.circ, mcap.realized, min.rev.usd, exch.flow.out.usd.incl, real.vol, telegram.users, txn.cnt, txn.tfr.erc721.cnt, exch.sply.ntv, sply.out, txn.tfr.val.med, mcap.out, reddit.active.users, exch.flow.out.usd, min.rev.ntv, txn.tfr.val.med.ntv |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-25 | True | None |
| end | End date. Default: Today | 2022-11-25 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

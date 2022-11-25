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
| timeseries | Messari timeseries id |  | True | exch.sply.ntv, sply.liquid, txn.vol, exch.flow.in.usd, reddit.active.users, mcap.realized, fees, diff.avg, txn.tsfr.cnt, real.vol, act.addr.cnt, exch.flow.out.ntv, mcap.out, nvt.adj.90d.ma, txn.tsfr.val.avg, exch.flow.in.ntv, hashrate, txn.tfr.val.med, txn.tfr.erc721.cnt, sply.total.iss, daily.vol, exch.flow.out.ntv.incl, reddit.subscribers, cg.sply.circ, exch.flow.in.ntv.incl, exch.flow.out.usd, exch.sply.usd, min.rev.ntv, txn.tfr.erc20.cnt, txn.tsfr.val.adj, txn.fee.avg.ntv, new.iss.usd, nvt.adj, fees.ntv, txn.cnt, new.iss.ntv, txn.fee.med, min.rev.usd, blk.size.bytes.avg, mcap.circ, sply.total.iss.ntv, txn.tfr.val.ntv, txn.tfr.avg.ntv, mcap.dom, price, sply.circ, exch.flow.in.usd.incl, sply.out, txn.tfr.val.med.ntv, daily.shp, txn.fee.med.ntv, blk.cnt, txn.fee.avg, blk.size.byte, exch.flow.out.usd.incl, iss.rate, txn.tfr.val.adj.ntv, telegram.users, twitter.followers |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-25 | True | None |
| end | End date. Default: Today | 2022-11-25 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

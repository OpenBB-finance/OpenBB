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
| timeseries | Messari timeseries id |  | True | sply.liquid, txn.tfr.avg.ntv, fees, reddit.subscribers, nvt.adj.90d.ma, exch.sply.usd, txn.cnt, diff.avg, min.rev.ntv, fees.ntv, exch.flow.in.ntv, txn.tfr.erc721.cnt, reddit.active.users, txn.fee.avg, txn.fee.avg.ntv, txn.tfr.val.adj.ntv, nvt.adj, txn.tsfr.val.avg, telegram.users, real.vol, sply.total.iss, txn.tfr.val.med, txn.tsfr.cnt, exch.flow.out.ntv.incl, mcap.circ, new.iss.usd, blk.cnt, exch.sply.ntv, exch.flow.in.usd, exch.flow.out.ntv, blk.size.bytes.avg, blk.size.byte, twitter.followers, exch.flow.in.usd.incl, mcap.dom, cg.sply.circ, mcap.realized, sply.total.iss.ntv, daily.vol, exch.flow.in.ntv.incl, txn.tsfr.val.adj, iss.rate, txn.tfr.val.med.ntv, sply.circ, txn.tfr.val.ntv, min.rev.usd, exch.flow.out.usd.incl, hashrate, act.addr.cnt, txn.fee.med, price, new.iss.ntv, exch.flow.out.usd, daily.shp, txn.tfr.erc20.cnt, txn.fee.med.ntv, mcap.out, txn.vol, sply.out |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

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
| timeseries | Messari timeseries id |  | True | exch.flow.in.ntv, txn.tfr.avg.ntv, sply.circ, hashrate, exch.flow.out.ntv.incl, txn.tfr.val.med.ntv, twitter.followers, txn.tfr.val.adj.ntv, txn.tsfr.val.adj, blk.size.byte, mcap.dom, txn.vol, reddit.active.users, exch.flow.in.ntv.incl, sply.total.iss.ntv, nvt.adj, act.addr.cnt, diff.avg, sply.liquid, exch.sply.ntv, txn.fee.avg.ntv, reddit.subscribers, fees.ntv, exch.flow.out.usd.incl, price, daily.shp, txn.tsfr.val.avg, blk.size.bytes.avg, exch.flow.in.usd, txn.tfr.erc20.cnt, daily.vol, exch.sply.usd, exch.flow.out.ntv, new.iss.usd, blk.cnt, nvt.adj.90d.ma, mcap.realized, cg.sply.circ, exch.flow.out.usd, txn.fee.med.ntv, min.rev.usd, fees, exch.flow.in.usd.incl, min.rev.ntv, telegram.users, txn.tfr.val.med, mcap.out, new.iss.ntv, txn.cnt, real.vol, iss.rate, sply.total.iss, txn.tfr.erc721.cnt, txn.tfr.val.ntv, txn.tsfr.cnt, txn.fee.med, txn.fee.avg, mcap.circ, sply.out |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-23 | True | None |
| end | End date. Default: Today | 2022-11-23 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

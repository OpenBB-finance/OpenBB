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
| timeseries | Messari timeseries id |  | True | exch.flow.out.usd.incl, txn.tfr.erc721.cnt, txn.fee.avg.ntv, nvt.adj.90d.ma, txn.fee.med, exch.flow.out.ntv, txn.tfr.val.ntv, twitter.followers, reddit.active.users, blk.size.bytes.avg, exch.sply.ntv, new.iss.usd, mcap.realized, real.vol, sply.circ, txn.vol, txn.tsfr.val.adj, price, exch.flow.in.usd.incl, fees, sply.liquid, mcap.out, telegram.users, txn.fee.avg, blk.size.byte, nvt.adj, mcap.dom, reddit.subscribers, new.iss.ntv, sply.total.iss.ntv, min.rev.ntv, fees.ntv, txn.tfr.avg.ntv, daily.vol, min.rev.usd, exch.flow.in.usd, exch.sply.usd, iss.rate, txn.cnt, txn.tsfr.val.avg, diff.avg, exch.flow.out.usd, txn.tfr.val.med.ntv, mcap.circ, exch.flow.in.ntv, cg.sply.circ, blk.cnt, txn.tsfr.cnt, txn.tfr.val.med, txn.tfr.erc20.cnt, exch.flow.out.ntv.incl, hashrate, sply.total.iss, exch.flow.in.ntv.incl, act.addr.cnt, txn.fee.med.ntv, txn.tfr.val.adj.ntv, sply.out, daily.shp |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

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
| timeseries | Messari timeseries id |  | True | diff.avg, txn.fee.avg.ntv, txn.fee.avg, exch.sply.usd, sply.circ, reddit.subscribers, txn.fee.med, exch.flow.out.ntv.incl, nvt.adj.90d.ma, blk.size.byte, min.rev.usd, exch.flow.out.usd.incl, exch.flow.in.ntv.incl, txn.cnt, new.iss.usd, sply.total.iss.ntv, txn.tfr.val.med.ntv, real.vol, blk.cnt, exch.flow.in.usd.incl, exch.flow.in.ntv, daily.shp, telegram.users, fees.ntv, cg.sply.circ, mcap.realized, mcap.dom, mcap.circ, exch.flow.out.ntv, txn.tfr.val.med, reddit.active.users, price, daily.vol, txn.tfr.avg.ntv, sply.liquid, exch.flow.in.usd, exch.sply.ntv, mcap.out, txn.tfr.erc721.cnt, nvt.adj, txn.tsfr.val.adj, txn.tfr.erc20.cnt, hashrate, min.rev.ntv, blk.size.bytes.avg, exch.flow.out.usd, txn.tsfr.val.avg, sply.total.iss, txn.tsfr.cnt, txn.fee.med.ntv, txn.vol, iss.rate, txn.tfr.val.adj.ntv, fees, sply.out, txn.tfr.val.ntv, new.iss.ntv, twitter.followers, act.addr.cnt |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

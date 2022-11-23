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
| timeseries | Messari timeseries id |  | True | exch.flow.in.usd.incl, iss.rate, txn.vol, txn.fee.avg.ntv, txn.tsfr.cnt, txn.tfr.val.med, reddit.subscribers, exch.sply.ntv, txn.tfr.val.adj.ntv, sply.circ, daily.shp, min.rev.ntv, mcap.circ, txn.fee.avg, mcap.dom, exch.flow.out.ntv.incl, exch.sply.usd, sply.total.iss, real.vol, txn.tsfr.val.avg, txn.tfr.erc20.cnt, nvt.adj.90d.ma, sply.out, new.iss.usd, exch.flow.out.usd.incl, new.iss.ntv, telegram.users, exch.flow.out.ntv, sply.liquid, hashrate, txn.cnt, txn.fee.med.ntv, blk.size.byte, exch.flow.in.ntv.incl, min.rev.usd, diff.avg, sply.total.iss.ntv, mcap.realized, txn.fee.med, price, act.addr.cnt, reddit.active.users, txn.tfr.val.ntv, exch.flow.out.usd, txn.tfr.avg.ntv, exch.flow.in.ntv, cg.sply.circ, twitter.followers, mcap.out, fees.ntv, daily.vol, txn.tfr.erc721.cnt, blk.size.bytes.avg, blk.cnt, txn.tsfr.val.adj, txn.tfr.val.med.ntv, fees, exch.flow.in.usd, nvt.adj |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-23 | True | None |
| end | End date. Default: Today | 2022-11-23 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

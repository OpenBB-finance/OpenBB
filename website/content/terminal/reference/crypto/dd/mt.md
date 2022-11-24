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
| timeseries | Messari timeseries id |  | True | sply.total.iss, sply.total.iss.ntv, txn.fee.avg.ntv, blk.size.bytes.avg, exch.flow.out.usd.incl, iss.rate, fees.ntv, blk.size.byte, exch.flow.in.ntv, txn.fee.med, price, reddit.subscribers, hashrate, txn.tfr.erc20.cnt, txn.tsfr.val.adj, min.rev.usd, daily.shp, mcap.realized, exch.flow.in.usd, diff.avg, txn.tfr.val.adj.ntv, txn.fee.avg, twitter.followers, min.rev.ntv, daily.vol, mcap.circ, exch.sply.ntv, exch.flow.out.usd, fees, nvt.adj.90d.ma, new.iss.usd, exch.sply.usd, txn.tfr.val.med, exch.flow.out.ntv.incl, telegram.users, txn.tsfr.val.avg, exch.flow.in.ntv.incl, txn.vol, txn.fee.med.ntv, exch.flow.in.usd.incl, sply.out, txn.tfr.val.med.ntv, mcap.dom, new.iss.ntv, exch.flow.out.ntv, sply.circ, txn.tfr.erc721.cnt, sply.liquid, txn.cnt, mcap.out, real.vol, txn.tsfr.cnt, cg.sply.circ, nvt.adj, txn.tfr.val.ntv, reddit.active.users, act.addr.cnt, blk.cnt, txn.tfr.avg.ntv |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

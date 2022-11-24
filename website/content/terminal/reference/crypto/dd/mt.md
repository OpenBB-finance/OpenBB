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
| timeseries | Messari timeseries id |  | True | exch.flow.out.ntv, mcap.out, txn.fee.avg.ntv, mcap.realized, daily.shp, daily.vol, telegram.users, blk.cnt, real.vol, min.rev.ntv, nvt.adj, txn.tfr.val.med.ntv, nvt.adj.90d.ma, hashrate, txn.tfr.val.adj.ntv, reddit.subscribers, exch.flow.in.usd, cg.sply.circ, twitter.followers, exch.flow.out.ntv.incl, txn.fee.avg, exch.sply.ntv, reddit.active.users, exch.flow.out.usd, txn.tfr.erc20.cnt, exch.flow.out.usd.incl, txn.cnt, exch.flow.in.usd.incl, txn.fee.med.ntv, act.addr.cnt, diff.avg, sply.total.iss.ntv, sply.liquid, blk.size.bytes.avg, sply.circ, exch.flow.in.ntv.incl, price, txn.tsfr.cnt, iss.rate, blk.size.byte, txn.tfr.erc721.cnt, min.rev.usd, mcap.dom, sply.total.iss, new.iss.usd, txn.fee.med, txn.tfr.val.med, exch.flow.in.ntv, txn.tsfr.val.avg, txn.tsfr.val.adj, sply.out, txn.tfr.val.ntv, fees, fees.ntv, exch.sply.usd, txn.vol, new.iss.ntv, txn.tfr.avg.ntv, mcap.circ |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |

---

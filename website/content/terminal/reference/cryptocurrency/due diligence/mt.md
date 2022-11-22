---
title: mt
description: OpenBB Terminal Function
---

# mt

Display messari timeseries [Source: https://messari.io]

### Usage

```python
usage: mt [--list] [-t TIMESERIES] [-i {5m,15m,30m,1h,1d,1w}] [-s START] [-end END] [--include-paid] [-q QUERY [QUERY ...]]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| list | Flag to show available timeseries | False | True | None |
| timeseries | Messari timeseries id |  | True | price, daily.shp, exch.flow.out.ntv.incl, fees.ntv, iss.rate, txn.tfr.erc721.cnt, sply.liquid, exch.sply.usd, mcap.realized, real.vol, act.addr.cnt, fees, txn.fee.avg.ntv, txn.tfr.val.med.ntv, mcap.circ, mcap.out, txn.tfr.avg.ntv, blk.cnt, blk.size.bytes.avg, txn.tfr.val.ntv, exch.flow.in.ntv, exch.flow.out.usd, diff.avg, txn.vol, nvt.adj.90d.ma, new.iss.usd, min.rev.usd, txn.fee.avg, sply.circ, twitter.followers, nvt.adj, txn.tsfr.cnt, txn.tsfr.val.adj, exch.flow.in.usd, txn.tfr.val.med, exch.flow.out.ntv, cg.sply.circ, sply.total.iss, exch.sply.ntv, daily.vol, sply.out, txn.tfr.erc20.cnt, txn.tfr.val.adj.ntv, sply.total.iss.ntv, reddit.subscribers, mcap.dom, hashrate, txn.fee.med, txn.cnt, exch.flow.in.usd.incl, txn.fee.med.ntv, exch.flow.in.ntv.incl, exch.flow.out.usd.incl, new.iss.ntv, min.rev.ntv, reddit.active.users, blk.size.byte, txn.tsfr.val.avg, telegram.users |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-22 | True | None |
| end | End date. Default: Today | 2022-11-22 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |
---


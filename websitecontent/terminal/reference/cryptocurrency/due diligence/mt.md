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
| timeseries | Messari timeseries id |  | True | txn.vol, daily.vol, fees.ntv, exch.flow.out.usd.incl, blk.size.bytes.avg, txn.cnt, txn.fee.avg.ntv, txn.fee.med, txn.tfr.val.adj.ntv, exch.flow.out.ntv.incl, new.iss.ntv, mcap.circ, real.vol, txn.tsfr.val.adj, mcap.out, exch.flow.in.ntv.incl, txn.fee.avg, mcap.dom, reddit.subscribers, cg.sply.circ, reddit.active.users, txn.tfr.erc20.cnt, txn.tfr.val.med.ntv, nvt.adj.90d.ma, exch.flow.out.ntv, mcap.realized, txn.tfr.erc721.cnt, exch.flow.in.usd.incl, txn.tfr.val.ntv, min.rev.ntv, txn.fee.med.ntv, txn.tsfr.cnt, exch.sply.usd, price, hashrate, diff.avg, telegram.users, new.iss.usd, blk.cnt, sply.liquid, exch.sply.ntv, blk.size.byte, sply.out, iss.rate, exch.flow.in.usd, sply.circ, txn.tsfr.val.avg, txn.tfr.val.med, fees, exch.flow.out.usd, sply.total.iss, txn.tfr.avg.ntv, min.rev.usd, nvt.adj, daily.shp, twitter.followers, exch.flow.in.ntv, act.addr.cnt, sply.total.iss.ntv |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-22 | True | None |
| end | End date. Default: Today | 2022-11-22 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |
---


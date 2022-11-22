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
| timeseries | Messari timeseries id |  | True | txn.tfr.erc721.cnt, exch.flow.in.usd.incl, iss.rate, txn.fee.avg, txn.tfr.val.adj.ntv, min.rev.usd, twitter.followers, act.addr.cnt, telegram.users, txn.tfr.avg.ntv, blk.size.bytes.avg, blk.cnt, reddit.subscribers, real.vol, txn.fee.avg.ntv, exch.flow.out.ntv, txn.tfr.val.ntv, mcap.dom, fees, txn.tsfr.cnt, fees.ntv, nvt.adj, txn.vol, txn.tfr.val.med.ntv, min.rev.ntv, exch.sply.ntv, txn.tfr.val.med, price, blk.size.byte, txn.tfr.erc20.cnt, reddit.active.users, exch.flow.in.usd, txn.tsfr.val.avg, exch.flow.out.ntv.incl, sply.total.iss, exch.sply.usd, txn.cnt, txn.tsfr.val.adj, txn.fee.med, txn.fee.med.ntv, hashrate, mcap.realized, daily.vol, daily.shp, mcap.out, cg.sply.circ, new.iss.usd, exch.flow.in.ntv, exch.flow.out.usd, sply.total.iss.ntv, exch.flow.out.usd.incl, nvt.adj.90d.ma, sply.out, new.iss.ntv, exch.flow.in.ntv.incl, mcap.circ, sply.liquid, diff.avg, sply.circ |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-22 | True | None |
| end | End date. Default: Today | 2022-11-22 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |
---


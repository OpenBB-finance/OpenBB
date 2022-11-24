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
| timeseries | Messari timeseries id |  | True | fees.ntv, exch.flow.out.usd.incl, txn.tfr.val.adj.ntv, txn.tfr.val.ntv, exch.sply.usd, hashrate, exch.flow.in.ntv.incl, sply.liquid, txn.tfr.val.med.ntv, blk.cnt, sply.total.iss.ntv, diff.avg, txn.fee.med, blk.size.bytes.avg, blk.size.byte, nvt.adj.90d.ma, real.vol, exch.flow.out.ntv, sply.out, twitter.followers, exch.flow.out.usd, txn.tfr.erc721.cnt, iss.rate, min.rev.ntv, txn.vol, telegram.users, sply.total.iss, mcap.out, exch.flow.in.usd, txn.cnt, price, reddit.active.users, txn.tsfr.val.adj, new.iss.usd, nvt.adj, txn.tsfr.cnt, exch.flow.in.ntv, txn.tfr.avg.ntv, sply.circ, mcap.realized, mcap.dom, txn.tfr.erc20.cnt, exch.flow.out.ntv.incl, txn.tfr.val.med, fees, txn.fee.avg, txn.tsfr.val.avg, exch.sply.ntv, min.rev.usd, new.iss.ntv, daily.vol, reddit.subscribers, txn.fee.avg.ntv, mcap.circ, daily.shp, txn.fee.med.ntv, cg.sply.circ, act.addr.cnt, exch.flow.in.usd.incl |
| interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | Initial date. Default: A year ago | 2021-11-24 | True | None |
| end | End date. Default: Today | 2022-11-24 | True | None |
| include_paid | Flag to show both paid and free sources | False | True | None |
| query | Query to search across all messari timeseries |  | True | None |
---


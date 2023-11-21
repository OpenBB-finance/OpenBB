---
title: mt
description: This page provides detailed information about how to display Messari
  timeseries data, explaining the use of key parameters, available data frequency
  intervals, and how to query the timeseries. It is a resource for understanding and
  extracting meaningful insights from Messari data.
keywords:
- messari timeseries
- timeseries parameters
- data frequency intervals
- messari data sources
- timeseries query
- messari usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /dd/mt - Reference | OpenBB Terminal Docs" />

Display messari timeseries [Source: https://messari.io]

### Usage

```python wordwrap
mt [--list] [-t TIMESERIES] [-i {5m,15m,30m,1h,1d,1w}] [-s START] [-end END] [--include-paid] [-q QUERY [QUERY ...]]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| list | --list | Flag to show available timeseries | False | True | None |
| timeseries | -t  --timeseries | Messari timeseries id |  | True | exch.flow.out.usd, txn.fee.avg.ntv, price, real.vol, vol.exch, exch.flow.in.ntv.incl, new.iss.ntv, sply.total.iss, txn.tsfr.cnt, reddit.subscribers, reddit.active.users, exch.flow.out.ntv, diff.avg, blk.size.bytes.avg, blk.size.byte, exch.flow.in.usd, nvt.adj.90d.ma, mcap.circ, txn.fee.avg, txn.tsfr.val.adj, txn.fee.med.ntv, hashrate, telegram.users, exch.flow.out.usd.incl, new.iss.usd, txn.tfr.erc20.cnt, txn.tfr.val.ntv, txn.tfr.avg.ntv, txn.tfr.val.adj.ntv, txn.tsfr.val.avg, sply.out, txn.tfr.val.med.ntv, sply.circ, exch.flow.in.usd.incl, txn.tfr.val.med, iss.rate, exch.sply.ntv, mcap.out, blk.cnt, txn.fee.med, min.rev.ntv, daily.shp, mcap.realized, txn.cnt, fees, sply.liquid, twitter.followers, txn.vol, exch.flow.out.ntv.incl, price.exch, act.addr.cnt, exch.sply.usd, exch.flow.in.ntv, txn.tfr.erc721.cnt, fees.ntv, sply.total.iss.ntv, nvt.adj, mcap.dom, cg.sply.circ, daily.vol, min.rev.usd |
| interval | -i  --interval | Frequency interval | 1d | True | 5m, 15m, 30m, 1h, 1d, 1w |
| start | -s  --start | Initial date. Default: A year ago | 2022-11-21 | True | None |
| end | -end  --end | End date. Default: Today | 2023-11-21 | True | None |
| include_paid | --include-paid | Flag to show both paid and free sources | False | True | None |
| query | -q  --query | Query to search across all messari timeseries |  | True | None |

---

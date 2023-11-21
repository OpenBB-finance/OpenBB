---
title: fees
description: Cryptos where users pay most fees on [Source CryptoStats]
keywords:
- crypto.disc
- fees
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /disc/fees - Reference | OpenBB Terminal Docs" />

Cryptos where users pay most fees on [Source: CryptoStats]

### Usage

```python wordwrap
fees [--mc] [--tvl] [-d DATE] [-s SORTBY [SORTBY ...]] [-r]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| marketcap | --mc | Include the market cap rank | False | True | None |
| tvl | --tvl | Include the total value locked | False | True | None |
| date | -d  --date | Initial date. Default: yesterday | 2023-11-20 | True | None |
| sortby | -s  --sort | Sort by given column. Default: One Day Fees | One Day Fees | True | One Day Fees, Market Cap Rank |
| reverse | -r  --reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---

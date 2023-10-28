---
title: news
description: This page provides information on the documentation for the 'news' functionality
  in OpenBBTerminal. It enables users to customize their news type and limit the number
  of news to be displayed.
keywords:
- OpenBBTerminal documentation
- Customize News
- News types
- Limit News Display
- Stock News
- Python code for news customization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.disc.news - Reference | OpenBB SDK Docs" />

Gets news. [Source: SeekingAlpha]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/seeking_alpha_model.py#L199)]

```python
openbb.stocks.disc.news(news_type: str = "Top-News", limit: int = 5)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| news_type | str | From: Top-News, On-The-Move, Market-Pulse, Notable-Calls, Buybacks, Commodities, Crypto, Issuance, Global,<br/>Guidance, IPOs, SPACs, Politics, M-A, Consumer, Energy, Financials, Healthcare, MLPs, REITs, Technology | Top-News | True |
| limit | int | Number of news to display | 5 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| List[dict] | List of dict news |
---

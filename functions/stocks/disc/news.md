---
title: news
description: OpenBB SDK Function
---

# news

## stocks_disc_seeking_alpha_model.get_news

```python title='openbb_terminal/stocks/discovery/seeking_alpha_model.py'
def get_news(news_type: str, limit: int) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/seeking_alpha_model.py#L199)

Description: Gets news. [Source: SeekingAlpha]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| news_type | str | From: Top-News, On-The-Move, Market-Pulse, Notable-Calls, Buybacks, Commodities, Crypto, Issuance, Global,
Guidance, IPOs, SPACs, Politics, M-A, Consumer, Energy, Financials, Healthcare, MLPs, REITs, Technology | None | False |
| limit | int | Number of news to display | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| List[dict] | List of dict news |

## Examples


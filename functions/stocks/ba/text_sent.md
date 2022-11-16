---
title: text_sent
description: OpenBB SDK Function
---

# text_sent

## stocks_ba_reddit_model.get_sentiment

```python title='openbb_terminal/decorators.py'
def get_sentiment() -> float:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L1056)

Description: Find the sentiment of a post and related comments

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| post_data | list[str] | A post and its comments in string form | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| float | A number in the range [-1, 1] representing sentiment |

## Examples


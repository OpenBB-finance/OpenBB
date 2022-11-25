---
title: infer
description: OpenBB Terminal Function
---

# infer

Print quick sentiment inference from last tweets that contain the ticker. This model splits the text into character-level tokens and uses vader sentiment analysis. [Source: Twitter]

### Usage

```python
usage: infer [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | limit of latest tweets to infer from. | 100 | True | None |
---


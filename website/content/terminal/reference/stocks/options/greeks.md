---
title: greeks
description: OpenBB Terminal Function
---

# greeks

The greeks for a given option.

### Usage

```python
usage: greeks [-d DIVIDEND] [-r RISK_FREE] [-p] [-m MIN] [-M MAX] [-a]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| dividend | The dividend continuous rate | 0 | True | None |
| risk_free | The risk free rate | None | True | None |
| put | Whether the option is a put. | False | True | None |
| min | Minimum strike price to show. | None | True | None |
| max | Maximum strike price to show. | None | True | None |
| all | Whether to show all greeks. | False | True | None |
---


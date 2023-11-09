---
title: ah
description: This page provides information on how to retrieve After-Hours stock movers
  using a chosen screener with the command '/scr ah signal'. Examples and parameter
  details are included.
keywords:
- After-Hours stock movers
- screener preset
- /scr ah signal
- After-Hours Top Gainers
- After-Hours Top Losers
- After-Hours Most Active
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="screeners: ah - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve After-Hours stock movers according to a chosen screener.

### Usage

```python wordwrap
/scr ah signal
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| signal | screener preset | False | After-Hours Top Gainers (ahgainers), After-Hours Top Losers (ahlosers), After-Hours Most Active (ahmost_active) |


---

## Examples

```
/scr ah signal:After-Hours Top Gainers
```

---

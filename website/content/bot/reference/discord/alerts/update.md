---
title: update
description: This page provides description and usage of the 'update' command within
  the context of active alerts. It includes details on how to change the condition
  of an active alert, specifically for price alerts.
keywords:
- Update command
- Price alert
- Active alerts
- Update condition
- Deactivate alert
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alerts: update - Discord Reference | OpenBB Bot Docs" />

This command allows the user to update the condition on an active alert, such as changing the value of a price alert. The command will update the alert with the new condition and keep the alert active until it is manually deactivated or the alert's condition is met.

### Usage

```python wordwrap
/alerts update alerts condition price
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| alerts | Your active alerts | False | None |
| condition | Update condition for alert | False | Equal or Above (above or equal), Equal or Below (below or equal) |
| price | Update alert to this price | False | None |


---

## Examples

```
/alerts update alerts: condition: price:
```

---

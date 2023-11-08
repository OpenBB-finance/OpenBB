---
title: bigprintsdp
description: This documentation page discusses how to use the command /bigprintsdp
  to retrieve the largest combination of dark pool and block trades, providing a comprehensive
  view of market activities over a specified number of days. The page also covers
  usage, parameters, and examples of the command.
keywords:
- bigprintsdp command
- dark pool trades
- block trades
- market activities
- command usage
- command parameters
- command examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="darkpool: bigprintsdp - Telegram Reference | OpenBB Bot Docs" />

This command will retrieve the largest combination of dark pool and block trades over a specified amount of days. It will provide a comprehensive view of the biggest dark pool and block trades over the specified number of days and give the user an idea of the market activity over that period.

### Usage

```python wordwrap
/bigprintsdp days
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| days | Number of days to look back | False | None |


---

## Examples

```
/bigprintsdp 6
```

---

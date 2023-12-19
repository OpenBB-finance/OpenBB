---
title: lookup
description: A detailed guide on how to use the lookup command in python, showing
  parameters such as search_text, limit, and offset and their usage.
keywords:
- lookup command
- search_text
- limit
- offset
- command parameters
- usage guide
- coding documentation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/degiro/lookup /brokers - Reference | OpenBB Terminal Docs" />



### Usage

```python
lookup [-l LIMIT] [-o OFFSET] search_text
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| search_text | Name of the company or a text. | None | False | None |
| limit | Number of result expected (0 for unlimited). | 10 | True | None |
| offset | To use an offset. | 0 | True | None |

---

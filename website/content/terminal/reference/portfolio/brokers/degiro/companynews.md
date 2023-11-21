---
title: companynews
description: This page contains a guide on how to use the 'companynews' tool and set
  its parameters such as SYMBOL, which represents the company's ISIN code; LIMIT for
  the number of news to display; OFFSET to adjust the displayed news; and LANGUAGES
  to define the languages in which the news appears.
keywords:
- company news tool
- usage guide
- ISIN code
- news display
- display offset
- language settings
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio /brokers/degiro/companynews - Reference | OpenBB Terminal Docs" />



### Usage

```python wordwrap
companynews -s SYMBOL [-l LIMIT] [-o OFFSET] [-lang LANGUAGES]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| symbol | -s  --symbol | ISIN code of the company. | None | False | None |
| limit | -l  --limit | Number of news to display. | 10 | True | None |
| offset | -o  --offset | Offset of news to display. | 0 | True | None |
| languages | -lang  --languages | Languages of news to display. | en,fr | True | None |

---

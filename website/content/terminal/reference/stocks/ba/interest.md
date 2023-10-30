---
title: interest
description: This page serves as a user guide for the 'interest' feature which plots
  keywords or phrases over time versus stock price. It provides details on its usage,
  parameters, and provides illustrative execution results. Notable keywords that you
  could use to influence the plotted interest include topical phrases like 'COVID',
  'WW3', and 'NFT'. The source for this functionality is based on Google.
keywords:
- Interest
- Stock price
- Words
- Sentences
- Date
- Parameters
- Default
- Optional
- Start
- Words
- Choices
- Google
- COVID
- WW3
- NFT
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/ba/interest - Reference | OpenBB Terminal Docs" />

Plot interest over time of words/sentences versus stock price. [Source: Google]

### Usage

```python
interest [-s START] [-w WORDS]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| start | starting date (format YYYY-MM-DD) of interest | 2020-11-23 | True | None |
| words | Select multiple sentences/words separated by commas. E.g. COVID,WW3,NFT | None | True | None |

![interest](https://user-images.githubusercontent.com/25267873/157575723-23c55e4e-9e87-4647-b8fa-8ed9643f471f.png)

---

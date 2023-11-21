---
title: tsne
description: Documentation page about TSNE method for comparing similar companies,
  detailing usage, parameters, and examples. It describes how to implement TSNE method
  using sklearn in Python.
keywords:
- TSNE
- sklearn
- comparison
- similar companies
- parameters
- usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /ca/tsne - Reference | OpenBB Terminal Docs" />

Get similar companies to compare with using sklearn TSNE.

### Usage

```python wordwrap
tsne [-r LR] [-l LIMIT] [-p]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| lr | -r  --learnrate | TSNE Learning rate. Typical values are between 50 and 200 | 200 | True | None |
| limit | -l  --limit | Limit of stocks to retrieve. The subsample will occur randomly. | 10 | True | None |
| no_plot | -p  --no_plot |  | False | True | None |

![tsne](https://user-images.githubusercontent.com/46355364/154074416-af8c7d2a-fa2f-461f-8522-933cf6e3543b.png)

---

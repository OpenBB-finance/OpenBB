---
title: tr
description: Documentation on how to display top repositories using the GitHub API.
  Instructions include usage, parameters details, and examples. The user can sort
  the repos by stars or forks, and can filter by repo categories.
keywords:
- top repositories
- github api
- parameters
- stars
- forks
- repo categories
- filter
- sort
- usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt/oss/tr - Reference | OpenBB Terminal Docs" />

Display top repositories [Source: https://api.github.com]

### Usage

```python
tr [-s {stars,forks}] [-c CATEGORIES]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| sortby | Sort repos by {stars, forks}. Default: stars | stars | True | stars, forks |
| categories | Filter by repo categories. If more than one separate with a comma: e.g., finance,investment |  | True | None |

![cases](https://user-images.githubusercontent.com/46355364/153897646-99e4f73f-be61-4ed7-a31d-58e8695e7c50.png)

---

---
title: query_graph
description: This page provides a detailed explanation of the query_graph helper methods
  for querying a graphql api, including the Python source code and parameters required,
  from openbb.crypto.onchain.query_graph. The response data is a dictionary.
keywords:
- query_graph
- helper methods
- graphql api
- bitquery.io
- openbb.crypto.onchain.query_graph
- parameters
- url
- query
- returns
- dictionary response data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.onchain.query_graph - Reference | OpenBB SDK Docs" />

Helper methods for querying graphql api. [Source: https://bitquery.io/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_model.py#L159)]

```python
openbb.crypto.onchain.query_graph(url: str, query: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| url | str | Endpoint url | None | False |
| query | str | Graphql query | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| dict | Dictionary with response data |
---

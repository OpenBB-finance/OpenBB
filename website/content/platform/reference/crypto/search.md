---
title: search
description: The documentation page provides information on how to perform a cryptocurrency
  search, including the search query and provider parameters, as well as the resulting
  crypto search data such as symbol, name, currency, and exchange information.
keywords:
- cryptocurrency search
- available cryptocurrency pairs
- python obb crypto search
- search query parameter
- provider parameter
- crypto search results
- crypto search provider
- crypto search warnings
- crypto search chart
- crypto search metadata
- crypto data
- symbol
- crypto name
- crypto currency
- crypto exchange
- crypto exchange name
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Cryptocurrency Search. Search available cryptocurrency pairs.

```python wordwrap
obb.crypto.search(query: str, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[CryptoSearch]
        Serializable results.

    provider : Optional[Literal['fmp']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. (Crypto) |
| name | str | Name of the crypto. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. (Crypto) |
| name | str | Name of the crypto. |
| currency | str | The currency the crypto trades for. |
| exchange | str | The exchange code the crypto trades on. |
| exchange_name | str | The short name of the exchange the crypto trades on. |
</TabItem>

</Tabs>


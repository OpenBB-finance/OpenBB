<!-- markdownlint-disable MD041 -->

Look up institutions regulated by the SEC.

```excel wordwrap
=OBB.REGULATORS.SEC.INSTITUTIONS_SEARCH(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: sec | true |
| query | string | Search query. | true |
| use_cache | boolean | Whether or not to use cache. If True, cache will store for seven days. (provider: sec) | true |

## Data

| Name | Description |
| ---- | ----------- |
| name | The name of the institution. (provider: sec) |
| cik | Central Index Key (CIK) (provider: sec) |

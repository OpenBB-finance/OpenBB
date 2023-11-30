<!-- markdownlint-disable MD041 -->

The RSS feed provides links to litigation releases concerning civil lawsuits brought by the Commission in federal court.

```excel wordwrap
=OBB.REGULATORS.SEC.RSS_LITIGATION(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: sec | true |

## Data

| Name | Description |
| ---- | ----------- |
| published | The date of publication. (provider: sec) |
| title | The title of the release. (provider: sec) |
| summary | Short summary of the release. (provider: sec) |
| id | The identifier associated with the release. (provider: sec) |
| link | URL to the release. (provider: sec) |

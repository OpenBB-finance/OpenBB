---
title: rss_litigation
description: Learn how to use the RSS feed to access litigation releases, including
  civil lawsuits brought by the Commission in federal court. This documentation provides
  details about the 'obb.regulators.sec.rss_litigation' python function, its parameters
  and return values, as well as the data structure used for the releases.
keywords: 
- RSS feed
- litigation releases
- civil lawsuits
- Commission
- federal court
- python
- obb.regulators.sec.rss_litigation
- provider
- parameters
- returns
- data
- published
- title
- summary
- id
- link
---

<!-- markdownlint-disable MD041 -->

The RSS feed provides links to litigation releases concerning civil lawsuits brought by the Commission in federal court.

## Syntax

```excel wordwrap
=OBB.REGULATORS.SEC.RSS_LITIGATION(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: sec | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| published | The date of publication. (provider: sec) |
| title | The title of the release. (provider: sec) |
| summary | Short summary of the release. (provider: sec) |
| id | The identifier associated with the release. (provider: sec) |
| link | URL to the release. (provider: sec) |

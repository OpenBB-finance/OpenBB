---
title: commands manage
description: Documentation on how to use the 'commands manage' command for autoposts
  on Discord. This includes its usage, parameters, and examples for removing or listing
  feeds.
keywords:
- commands manage
- autopost command
- Discord autoposts
- manage autoposts
- remove autoposts
- autopost parameters
- autopost usage
- list autoposts
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="autopost: commands manage - Discord Reference | OpenBB Bot Docs" />

This command allows the user to remove an autopost webhook feed from the channel. When executed, it will remove the feed from the channel and prevent any further autoposts from being sent.

### Usage

```python wordwrap
/autopost commands manage action
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| action | Remove, or List your feeds for Discord autoposts | True | Remove, List |

---

## Examples

```
/autopost commands manage action:List
```

```
/autopost commands manage action:Remove
```

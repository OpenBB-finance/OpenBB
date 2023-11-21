---
title: askobb
description: Accept input as a string and return the most appropriate Terminal command
keywords:
- account
- askobb
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="account /askobb - Reference | OpenBB Terminal Docs" />

Accept input as a string and return the most appropriate Terminal command

### Usage

```python wordwrap
askobb [--prompt QUESTION [QUESTION ...]] [--model {gpt-3.5-turbo,gpt-4}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| question | --prompt  -p | Question for Askobb LLM |  | True | None |
| gpt_model | --model  -m | GPT Model to use for Askobb LLM (default: gpt-3.5-turbo) or gpt-4 (beta) | gpt-3.5-turbo | True | gpt-3.5-turbo, gpt-4 |

---

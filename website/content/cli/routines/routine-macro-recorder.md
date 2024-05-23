---
title: Routine Macro Recorder
sidebar_position: 4
description: Learn how to use the macro recorder in OpenBB to start saving commands
  and automate common tasks with scripts. This page guides you through the process
  of recording, saving, and accessing your recorded routines.
keywords:
- macro recorder
- script routines
- global commands
- command recording
- routine script
- terminal main menu
- exe --file
- OpenBBUserData
- routines folder
- cli
- record
- stop
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Routine Macro Recorder - Routines - Usage | OpenBB Platform CLI Docs" />

OpenBB script routines can be captured with the macro recorder, controlled with global commands. Enter, `record`, to start saving commands, and then, `stop`, terminates the recording. This means that any command you run will be captured in the script; and on `stop`, it will be saved to the `~/OpenBBUserData/routines/` folder.

For example:

```console
record -n sample

/equity/price/historical --symbol SPY --provider cboe --interval 1m/home/derivatives/options/chains --symbol SPY --provider cboe/home/stop/r
```

The final command after `stop`, `r`, resets the CLI so that the routine is presented as a choice in the `exe` command.

It can now be played back by entering:

```console
/exe --file sample.openbb
```

:::tip
The routine can be edited to replace parameter values with input variables - e.g, `$ARGV[0]`, `$ARGV[1]`, etc.
:::

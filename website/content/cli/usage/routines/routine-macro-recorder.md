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
- Excel's VBA methods
- command recording
- routine script
- terminal main menu
- exe --file
- OpenBBUserData
- routines folder
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Routine Macro Recorder - Routines - Usage | OpenBB CLI Docs" />

OpenBB script routines can be captured with the macro recorder, controlled with global commands, `record` to start saving commands and `stop` to terminate the recording. This shares similarities with that of Excel's VBA methods. This means that any command you run will be automatically recorded for the routine script and once you type `stop` it automatically saves the file to the `~/OpenBBUserData/routines/` folder.

For example, if you copy and paste the following prompt in the OpenBB Platform CLI and press enter, you will see an example.

```console

```

The following shows the output from this pipeline of commands.

Because there was a `record` and `stop` at the `start` and `end` respectively, a routine script was created. This file cane be found inside the `routines` folder within the `OpenBBUserData` folder (more on exporting and import data [here](/terminal/usage/data/custom-data)).

Now, you should be able to access the routine file from the CLI main menu by doing `/exe --file` and using the auto-completer. Note that the naming of the file will differ for you based on the time you are executing the script.

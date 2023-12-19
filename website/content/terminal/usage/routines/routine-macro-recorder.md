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

<HeadTitle title="Routine Macro Recorder - Routines - Usage | OpenBB Terminal Docs" />

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
    youtubeLink="https://www.youtube.com/embed/o53onlk7tPw?si=VPBKE_V3U1WNH-QO"
    videoLegend="Short video on recording commands to create routine"
/>

OpenBB script routines can be captured with the macro recorder, controlled with global commands, `record` to start saving commands and `stop` to terminate the recording. This shares similarities with that of Excel's VBA methods. This means that any command you run will be automatically recorded for the routine script and once you type `stop` it automatically saves the file to the `~/OpenBBUserData/routines/` folder.

For example, if you copy and paste the following prompt in the OpenBB Terminal and press enter, you will see an example.

```console
/record/economy/cpi/treasury/index sp500/stop
```

The following shows the output from this pipeline of commands.

![Routines](https://user-images.githubusercontent.com/46355364/223204998-70d9e5da-f84e-4c22-90c4-576dcf87c1df.png)

Because there was a `record` and `stop` at the `start` and `end` respectively, a routine script was created. This file cane be found inside the `routines` folder within the `OpenBBUserData` folder (more on exporting and import data [here](/terminal/usage/data/custom-data)).

Now, you should be able to access the routine file from the terminal main menu by doing `/exe --file` and using the auto-completer. Note that the naming of the file will differ for you based on the time you are executing the script.

![Routines](https://user-images.githubusercontent.com/46355364/223205394-77e7a33d-e9fa-4686-b32f-e8d183b265e6.png)

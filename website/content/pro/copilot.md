---
title: Copilot
sidebar_position: 7
description: Learn how to use OpenBB Copilot to interact with the OpenBB Terminal Pro
keywords:
- OpenBB Copilot
- voice command
- change theme mode
- load templates
- TSLA
- Natural language processing
- Large language model
- OpenAI
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';
import ReactPlayer from 'react-player'


<HeadTitle title="Copilot | OpenBB Terminal Pro Docs" />

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<!-- <TutorialVideo -->
<!--   youtubeLink="https://www.youtube.com/embed/ZdIZ4dOG9tE?si=dKAanLAC84eVKcyD" -->
<!--   videoLegend="Short introduction to copilot" -->
<!-- /> -->

OpenBB copilot is your companion to interact with the OpenBB Terminal Pro.


<!-- <img className="pro-border-gradient" width="3701" alt="COPILOT- New" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/1c2d892e-03b7-4db8-9e8c-6fb1ab8512a1" /> -->

## Getting started

<ReactPlayer width="50%" height="50%" playing loop muted='true' volume='0' url='https://github.com/OpenBB-finance/OpenBBTerminal/assets/14093308/6466c3e3-111b-4246-ae9b-b6403712c862' />

To open OpenBB Copilot, click on the icon located at the bottom right of the Terminal Pro screen.

You can interact with OpenBB Copilot either through typing text or using your
voice.  Under most circumstances, you can treat OpenBB Copilot like your very
own personal research assistant. OpenBB Copilot can answer general financial
questions, use the data displayed in the dashboard to perform analytical tasks,
and even interact with files that you choose to upload.

We'll be exploring each of these features in the sections below.

## Understanding chat history

<ReactPlayer width="50%" height="100%" playing loop muted='true' volume='0' url='https://github.com/OpenBB-finance/OpenBBTerminal/assets/14093308/312510fb-fb17-474c-8698-a2960134e285' />

OpenBB Copilot is a conversational agent. This means that OpenBB Copilot uses
previous messages and answers in the current chat to help answer your query.
This means you can guide OpenBB Copilot to perform the task you want, or ask
follow-up questions.

In the example above, the user first asked about the Price-to-earnings (P/E)
ratio. After OpenBB Copilot was done answering the question, the user asked a
follow-up question regarding additional ratios that may be important. Since
OpenBB Copilot is aware of the chat history of the current conversation, it
proceeded to answer the user's query within the context of the conversation
(financial ratios) by suggesting other important financial ratios that might be
of use to the user.

If you'd like to clear the history of the current conversation, you can do so by
clicking on the bin icon in the OpenBB Copilot chatbox. It is usually a good
idea to clear the chat history when you have a new question that is unrelated to
your current conversation.

<ReactPlayer width="50%" height="100%" playing loop muted='true' volume='0' url='https://github.com/OpenBB-finance/OpenBBTerminal/assets/14093308/dd67030e-bfd4-4e8c-b9f4-e67d3dbd2249' />


## General question answering
As seen in the previous section, OpenBB Copilot is capable of answering general
financial questions and answers.  For example, you can ask Copilot things like:

- "What's the difference between stocks and bonds?"
- "Explain inflation"
- "Can you explain the concept of dollar-cost averaging?"

For general financial questions, OpenBB Copilot will rely on the underlying
model's extensive training data to formulate answers. We encourage users to
explore with in-depth and varied questions.

## Querying the dashboard

<ReactPlayer width="70%" height="100%" playing loop muted='true' volume='0' url='https://github.com/OpenBB-finance/OpenBBTerminal/assets/14093308/0c502fa9-dae3-45f1-996d-2b9940161c24' />

By default, OpenBB Copilot has access to the same data that is displayed on your
currently-selected dashboard. This means that OpenBB Copilot can answer queries
related to any information currently residing in your dashboard.

In the example above, the user asked OpenBB Copilot to summarize the current
news regarding Apple. Since the Company News widget is present in the
dashboard, and is currently configured to display news for AAPL (Apple Inc.),
OpenBB Copilot autonomously understands and retrieves this data, using it to
answer the user's query.

It's important to understand which data was used by OpenBB Copilot to formulate
an answer. As a result, OpenBB Copilot will cite which data source it utilized
in order to answer the user's query, as shown below:

<ReactPlayer width="50%" height="100%" playing loop muted='true' volume='0' url='https://github.com/OpenBB-finance/OpenBBTerminal/assets/14093308/2156f1cb-f49e-4481-8131-41fcd6b91672' />

Since OpenBB Copilot can access data from any widget in the active dashboard, we
encourage users to experiment with adding different kinds of widgets. For
example, OpenBB Copilot is particularly effective at summarizing earnings call
transcripts from the "Earnings Transcripts" widget.

## Focus on specific widgets

## Bring your own files


The scope of your request can range from basic commands such as "change theme mode to light", to more intricate requests like "load my equity template with TSLA" or "Add insider trading and ownership widgets to this dashboard".

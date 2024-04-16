---
title: OpenBB Copilot
sidebar_position: 8
description: Learn how to use OpenBB Copilot to interact with the OpenBB Terminal Pro
keywords:
- OpenBB Copilot
- copilot
- voice command
- agent
- assistant
- Natural language processing
- Large language model
- OpenAI
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';
import ReactPlayer from 'react-player'


<HeadTitle title="Copilot | OpenBB Terminal Pro Docs" />

OpenBB copilot is your companion to interact with the OpenBB Terminal Pro.

## Getting started

<ReactPlayer width="50%" height="50%" playing loop muted='true' volume='0' url='https://github.com/OpenBB-finance/OpenBBTerminal/assets/14093308/6466c3e3-111b-4246-ae9b-b6403712c862' />

To open OpenBB Copilot, click on the icon located at the bottom right of the
Terminal Pro screen.

You can interact with OpenBB Copilot either through typing text or using your
voice.  Under most circumstances, you can treat OpenBB Copilot like your very
own personal research assistant. OpenBB Copilot can answer general financial
questions, use the data displayed in the dashboard to perform analytical tasks,
and even interact with files that you choose to upload.

We'll be exploring each of these features in the following sections below.

## Understanding chat history

<ReactPlayer width="50%" height="100%" playing loop muted='true' volume='0' url='https://github.com/OpenBB-finance/OpenBBTerminal/assets/14093308/312510fb-fb17-474c-8698-a2960134e285' />

OpenBB Copilot is a conversational agent. This means that OpenBB Copilot uses
previous messages and answers in the current chat to help answer your query.
This allows you to guide OpenBB Copilot to perform the task you want, or ask
follow-up questions.

In the example above, the user first asked about the price-to-earnings (P/E)
ratio. After OpenBB Copilot answered the question, the user asked a
follow-up question regarding additional ratios that may be important. Since
OpenBB Copilot is aware of the context of the current conversation, it
proceeded to answer the user's query within the context of the conversation
(in this case, financial ratios) by suggesting other important financial ratios that might be
of use.

If you'd like to clear the history of the current conversation, you can do so by
clicking on the trashcan icon in the OpenBB Copilot chatbox. It is usually a good
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
explore this functionality with in-depth and varied questions.

## Querying the dashboard

<ReactPlayer width="70%" height="100%" playing loop muted='true' volume='0' url='https://github.com/OpenBB-finance/OpenBBTerminal/assets/14093308/0c502fa9-dae3-45f1-996d-2b9940161c24' />

By default, OpenBB Copilot has access to the same data that is displayed on your
currently-active dashboard. This means that OpenBB Copilot can answer queries
related to any information or data that is visible.

In the example above, the user asked OpenBB Copilot to summarize the current
news regarding Apple. Since the Company News widget is present in the
dashboard, and is currently configured to display news for AAPL (Apple Inc.),
OpenBB Copilot automatically understands and retrieves this data, using it to
answer the user's query.

It's important to understand which data was used by OpenBB Copilot to formulate
an answer. As a result, OpenBB Copilot will cite which data source it utilized
in order to answer the user's query.

<ReactPlayer width="50%" height="100%" playing loop muted='true' volume='0' url='https://github.com/OpenBB-finance/OpenBBTerminal/assets/14093308/2156f1cb-f49e-4481-8131-41fcd6b91672' />

Since OpenBB Copilot can access data from any widget in the active dashboard, we
encourage users to experiment with adding different kinds of widgets and
experimenting with various queries. For example, OpenBB Copilot is particularly
effective at summarizing earnings call transcripts from the "Earnings
Transcripts" widget.

## Querying specific widgets only

<ReactPlayer width="70%" height="100%" playing loop muted='true' volume='0' url='https://github.com/OpenBB-finance/OpenBBTerminal/assets/14093308/1335e310-cd65-4917-bc34-1de8b3e5f7fc' />


Sometimes you may wish to focus your analysis and utilize OpenBB Copilot to analyze only
 a specific subset of widgets. For example, you may want to use OpenBB Copilot
 is assist you in a deep analysis of an earnings transcript in the "Earnings
 Transcript" widget, without retrieving data from the rest of the dashboard.

 To achieve this, you can chat with specifically selected widgets by clicking on
 the "Add widgets as context" button on each widget you wish to use while
 querying OpenBB Copilot. Selecting a widget in this manner will make that
 widget's data available to OpenBB Copilot, while excluding other widgets that
 have not been selected. You can then use OpenBB Copilot as normal, and the
 unselected widgets in the rest of the dashboard will be ignored by OpenBB
 Copilot.

## Querying your own data

<ReactPlayer width="70%" height="100%" playing loop muted='true' volume='0' url='https://github.com/OpenBB-finance/OpenBBTerminal/assets/14093308/905eb674-5619-4797-8adf-9cf13a846792' />

OpenBB Copilot can also answer queries using files that you provide. Currently
TXT, PDF, CSV and XLSX files are supported. Files can be added to the Copilot by
dragging and dropping them on the OpenBB Copilot chatbox, or by clicking the
paper clip icon.

Once your files have been uploaded, OpenBB Copilot will use the data in the
uploaded files, if necessary, to answer your queries. If OpenBB Copilot uses the data
contained in your files to answer a query, it will cite which files it used (and
in the case of PDFs, the specific page).

:::note

OpenBB Copilot makes use of filenames to assess whether a file is
relevant to the user's query. As a result, it is highly recommended that you use
filenames that are descriptive of the data that they contain. For example, given
a PDF file containing a technical report from TSLA released in 2024, a good
filename would be `tsla_technical_report_2024.pdf`.

:::

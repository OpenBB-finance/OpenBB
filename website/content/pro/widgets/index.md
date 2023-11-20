---
title: Widgets
sidebar_position: 0
description: The page contains detailed information about the interactive elements
  and functionalities of OpenBB Terminal Pro widgets. From grouping mechanisms to
  settings, these widgets offer an interactive dashboard experience for users to track
  and analyze their investments and data. The widgets support both raw data and chart
  interpretations for data visualization.
keywords:
- Widgets
- Upper Tab
- Interactive elements
- Additional information
- Symbol
- Group
- Staleness Indicator
- Chat with Widget
- Grouping Mechanism
- Settings
- Close
- Content
- Raw Data
- Charts
- Interactive dashboard
- Investment positions
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Widgets | OpenBB Terminal Pro Docs" />

<img width="616" alt="275681758-87fda536-c62c-4b3b-a6c0-42b4b2a3a3cc" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/42b9321b-2912-4853-af1e-abb256573fec"/>

## Upper Tab

The upper tab houses all the interactive elements and additional information related to the widget's content.

### Left Side

#### Title

The title identifies the widget and is used when adding the same widget to another dashboard via advanced search.

#### Symbol

Some widgets are associated with a symbol. Changing this symbol updates the table content to reflect the new symbol.

#### Group

The group (if any) that the widget belongs to. If multiple widgets belong to the same group, updating the symbol in one will automatically update the symbol in the others.

### Right Side

#### Staleness Indicator

This indicator shows the freshness of the data:

* Green - updated within the last 30 seconds

* Yellow - updated between 30 seconds and 5 minutes ago

* Red - updated over 5 minutes ago

#### Chat with Widget

Our proprietary generative AI feature allows you to interact with the widget. Ask it to summarize its contents or explain how its data could impact your investment positions.

#### Grouping Mechanism

This feature allows you to group widgets together. When widgets are grouped, they share a color and number. You can see which dashboards have which groupings by looking at the text below the dashboard title in the sidebar.

#### Settings

<img width="623" alt="275681803-98815926-3d46-4555-a81a-8832c1b50a05" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/c3b35a8f-2188-48b0-89a7-17c03a2dbe37"/>

* Settings - View the data source and select or hide columns.
* Share - Share this widget with your team.
* Duplicate - Create a copy of this widget on the same dashboard.
* Export - Export data in various formats, such as csv, xlsx, png, or jpeg.
* Maximize - View the widget in full-screen mode.
* Copy to - Copy the widget to a different dashboard.

#### Close

This option removes the widget from the dashboard.

## Content

OpenBB widgets support two main types of content:

#### Raw Data

Displayed in a table format. This is powerful as it allows to leverage the charting from raw data capabilities of the application.

<img width="883" alt="275682032-e314c938-8069-4bf1-9aea-a0c2e4e239ff" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/9a481f04-7ba1-45bb-84c3-0eed3da68eca"/>


#### Charts

Visual representations of data, including line charts, bar charts, pie charts, and other custom charts. Some examples below,

<img width="620" alt="275682286-bb6b2323-afec-42ff-bbc0-f07f92e8978e" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/d235fec9-8c82-46d3-b226-d67c8b86a5c9"/>

<img width="621" alt="275682325-d8c1a586-3348-4814-b2e6-20930822de7a" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/05fe6a91-8f87-49fa-a050-9bfe2a4cadb5"/>

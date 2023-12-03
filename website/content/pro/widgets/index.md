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

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
  youtubeLink="https://www.youtube.com/embed/_kg8bCTNM14?si=OLAa1ehCEm57SFjd"
  videoLegend="Short introduction to widgets"
/>

## Upper Tab

<img className="pro-border-gradient" width="800" alt="Widget-rev" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/97943512-5488-4e94-8a06-b59ec6e51e4c" />

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

<img className="pro-border-gradient" width="800" alt="Widget settings" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/aaef053c-dacb-4f92-af02-583b4924a546" />

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

<img className="pro-border-gradient" width="800" alt="dividend" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/a71c683a-92df-4e5b-9ce3-1f8a91b9dcfc" />

#### Charts

Visual representations of data, including line charts, bar charts, pie charts, and other custom charts. Some examples below,

<img className="pro-border-gradient" width="800" alt="newswidget" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/5ada7e7f-c619-46fb-850f-006c6e0d0cd2" />

<img className="pro-border-gradient" width="800" alt="widget-revbiz" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/bbc0b737-ce03-4241-acaa-ad6b71c2a5ba" />

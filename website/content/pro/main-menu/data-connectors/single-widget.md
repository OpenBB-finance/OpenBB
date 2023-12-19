---
title: Single widget
sidebar_position: 1
description: Learn how to use the Single Widget of OpenBB Terminal Pro for seamless
  integration with your API Endpoints, enabling custom data to be fetched and displayed
  in an accessible format. Includes features like additional headers and addressing
  nested JSON data.
keywords:
- Single Widget
- Data Connectors
- API Endpoints
- Data Integration
- User-friendly Table Format
- Additional Headers
- Data Key Parameter
- Nested JSON
- Custom Backend
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Single Widget | OpenBB Terminal Pro Docs" />

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
  youtubeLink="https://www.youtube.com/embed/gX63rYzqpL0?si=74No_7LgG2gYwnDg"
  videoLegend="Short introduction to adding a single widget"
/>

The single widget is the most straightforward method to integrate your custom data into OpenBB Terminal Pro. Simply paste your API endpoint into the data connectors tab, and voila! Your data is fetched and displayed in a user-friendly table format.

To use this feature, input your API endpoint and any necessary connection information. The widget will then dynamically load and present your data within the Terminal Pro interface.

If your endpoint requires additional headers, don't worry. You can easily add them using the '+ Add Additional Headers' button.

In addition, if your API endpoint doesn't return a a simple JSON but a nested architecture, you will be prompted with a "Data Key" parameter which you can use to grab the data of interest.

If you want to do something more custom, you should look into creating [your own backend](/pro/main-menu/data-connectors/integrate-your-own-backend), or reach out to OpenBB for support.

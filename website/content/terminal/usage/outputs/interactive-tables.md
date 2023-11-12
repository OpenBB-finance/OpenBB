---
title: Interactive Tables
sidebar_position: 1
description: Learn how to navigate and utilize OpenBB's interactive tables using our
  open source PyWry technology. Understand how to sort and filter columns, hide or
  remove columns, select number of rows per page, freeze index and column headers,
  and export the data.
keywords:
- interactive tables
- PyWry technology
- sorting columns
- filtering columns
- hiding columns
- rows per page
- freeze index
- freeze column headers
- exporting data
- data visualization
- customizing tables
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Interactive Tables - Outputs - Usage | OpenBB Terminal Docs" />

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
    youtubeLink="https://www.youtube.com/embed/knIYEvziZXQ?si=_2h8-xcodRm-qU6Y"
    videoLegend="Short introduction on interactive tables"
/>

A common type of output in OpenBB are interactive tables which open in a separated window (utilizing our [open source PyWry](https://github.com/OpenBB-finance/pywry) technology). These provide methods for searching, sorting, filtering, exporting and even adapting settings directly on the table.

<details>
<summary>Table cheat sheet </summary>

![Chart Intro (5)](https://user-images.githubusercontent.com/85772166/234315026-de098953-111b-4b69-9124-31530c01407a.png)

</details>

## Sorting

Columns can be sorted ascending/descending/unsorted, by clicking the controls to the right of each header title.  The status of the filtering is shown as a blue indicator.

![Sort Columns](https://user-images.githubusercontent.com/85772166/233248754-20c18390-a7af-490c-9571-876447b1b0ae.png)

## Filtering

The settings button, at the lower-left corner, displays choices for customizing the table. By selecting the `Type` to be `Advanced`, columns become filterable.

![Table Settings](https://user-images.githubusercontent.com/85772166/233248876-0d788ff4-974d-4d92-8186-56864469870a.png)

The columns can be filtered with min/max values or by letters, depending on the content of each column.

![Filtered Tables](https://user-images.githubusercontent.com/85772166/233248923-45873bf1-de6b-40f8-a4aa-05e7c3d21ab0.png)

## Hiding columns

The table will scroll to the right as far as there are columns.  Columns can be removed from the table by clicking the icon to the right of the settings button and unchecking it from the list.

![Select Columns](https://user-images.githubusercontent.com/85772166/233248976-849791a6-c126-437c-bb54-454ba6ea4fa2.png)

## Select rows per page

The number of rows per page is defined in the drop down selection near the center, at the bottom.

![Rows per Page](https://user-images.githubusercontent.com/85772166/233249018-8269896d-72f7-4e72-a4d4-2715d1f11b96.png)

## Freeze the Index and Column Headers

Right-click on the index name to enable/disable freezing when scrolling to the right. Column headers are frozen by default.

![Index Freeze](https://user-images.githubusercontent.com/85772166/234103702-0965dfbd-24ca-4a66-8c76-9fac28abcff8.png)

## Exporting Data

At the bottom-right corner of the table window, there is a button for exporting the data.  To the left, the drop down selection for `Type` can be defined as a CSV, XLSX, or PNG file.  Exporting the table as a PNG file will create a screenshot of the table at its current view, and data that is not visible will not be captured.

![Export Data](https://user-images.githubusercontent.com/85772166/233249065-60728dd1-612e-4684-b196-892f3604c0f4.png)

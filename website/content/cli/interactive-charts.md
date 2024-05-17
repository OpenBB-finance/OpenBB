---
title: Interactive Charts
sidebar_position: 9
description: This page provides a detailed explanation of the OpenBB Interactive Charts. Understand various capabilities including annotation, color modification, drawing tools, data export, and supplementary data overlay.
keywords:
- interactive charts
- PyWry
- annotation
- drawing
- lines
- modebar
- plotly
- data export
- data overlay
- editing chart title
- Toolbar
- Text Tools
- Draw Tools
- Export Tools
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Interactive Charts - | OpenBB Platform CLI Docs" />

Interactive charts open in a separate window ([PyWry](https://github.com/OpenBB-finance/pywry)). The OpenBB charting library provides interactive and highly customizable charts.

:::tip
Not all commands have a charting output, the ones that do, will display a chart argument (`--chart`), which will trigger the charting output instead of the default table output.

Example: `equity/price/historical --symbol AAPL --chart`
:::

<details>
<summary>Charting cheat sheet </summary>

![Group 653](https://user-images.githubusercontent.com/85772166/234313541-3d725e1c-ce48-4413-9267-b03571e0eccd.png)

</details>

## Toolbar

![Chart Tools](https://user-images.githubusercontent.com/85772166/233247997-55c03cbd-9ca9-4f5e-b3fb-3e5a9c63b6eb.png)

The toolbar is located at the bottom of the window, and provides methods for:

- Panning and zooming.
- Modifying the title and axis labels.
- Adjusting the hover read out.
- Toggling light/dark mode.
- Annotating and drawing.
- Exporting raw data.
- Saving the chart as an image.
- Adding supplementary external data as an overlay.

The label for each tool is displayed by holding the mouse over it.

The toolbar's visibility can be toggled utilizing the `ctrl + h` shortcut.

## Text Tools

Annotate a chart by clicking on the `Add Text` button, or with the keyboard, `ctrl + t`.

![Annotate Charts](https://user-images.githubusercontent.com/85772166/233248056-d459d7a0-ba2d-4533-896a-79406ded859e.png)

Enter some text, make any adjustments to the options, then `submit`.  Place the crosshairs over the desired data point and click to place the text.

![Place Text](https://user-images.githubusercontent.com/85772166/233728645-74734241-4da2-4cff-af17-b68a62e95113.png)

After placement, the text can be updated or deleted by clicking on it again.

![Delete Annotation](https://user-images.githubusercontent.com/85772166/233728428-55d2a8e5-a68a-4cd1-9dbf-4c1cd697187e.png)

## Change Titles

The title of the chart is edited by clicking the button, `Change Titles`, near the middle center of the toolbar, immediately to the right of the `Add Text` button.

## Draw Tools

![Edit Colors](https://user-images.githubusercontent.com/85772166/233729318-8af947fa-ce2a-43e2-85ab-657e583ac8b1.png)

The fourth group of icons on the toolbar are for drawing lines and shapes.

- Edit the colors.
- Draw a straight line.
- Draw a freeform line.
- Draw a circle.
- Draw a rectangle.
- Erase a shape.

To draw on the chart, select one of the four drawing buttons and drag the mouse over the desired area. Click on any existing shape to modify it by dragging with the mouse and editing the color, or remove it by clicking the toolbar button, `Erase Active Shape`. The edit colors button will pop up as a floating icon, and clicking on that will display the color palette.

## Export Tools

The two buttons at the far-right of the toolbar are for saving the raw data or, to save an image file of the chart at the current panned and zoomed view.

![Export Tools](https://user-images.githubusercontent.com/85772166/233248436-08a2a463-403b-4b1b-b7d8-80cd5af7bee3.png)

## Overlay

The button, `Overlay chart from CSV`, provides an easy import method for supplementing a chart with additional data.  Clicking on the button opens a pop-up dialogue to select the file, column, and whether the overlay should be a bar, candlestick, or line chart.  As a candlestick, the CSV file must contain OHLC data.  The import window can also be opened with the keyboard, `ctrl-o`.

![Overlay CSV](https://user-images.githubusercontent.com/85772166/233248522-16b539f4-b0ae-4c30-8c72-dfa59d0c0cfb.png)

After choosing the file to overlay, select what to show and then click on `Submit`.

![Overlay Options](https://user-images.githubusercontent.com/85772166/233250634-44864da0-0936-4d3c-8de2-c8374d26c1d2.png)

![Overlay Chart](https://user-images.githubusercontent.com/85772166/233248639-6d12b16d-471f-4550-a8ab-8d8c18eeabb3.png)

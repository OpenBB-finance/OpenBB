---
title: Grouping Mechanism
sidebar_position: 1
description: Learn about the powerful grouping mechanism in OpenBB Terminal Pro. Understand
  how widgets can be grouped based on equity categories and tickers, and also how
  the watchlist widget's unique grouping property works.
keywords:
- Grouping
- Widgets
- Ticker
- Symbol
- Dashboard
- Watchlist
- Relationship
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Grouping | OpenBB Terminal Pro Docs" />

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
  youtubeLink="https://www.youtube.com/embed/cOH8qjOBWTI?si=I_NLm7UP4vgNBjo4"
  videoLegend="Short introduction to grouping"
/>

The grouping mechanism is extremely powerful as it allows widgets to be grouped together through one of their parameters based on the category they belong to.

For instance, for the equity category, widgets can be connected through their ticker / symbol. Examples are: AAPL to simbolize Apple, TSLA for Tesla and so on.

<img className="pro-border-gradient" width="800" alt="grouping" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/f0cbeb52-c7cd-4e03-9eba-5ef35e1665b6" />

This is an example of 3 widgets that belong to the same group, note the dark yellow 1 on the top right.

In addition, when clicking on the grouping icon you can see that they are grouped around the MSFT ticker.

This means that if a user changes the ticker on any of these widgets, the remaining ones will get updated accordingly.

Also note that the grouping is visible on the sidebar, immediately under the dashboard naming.

A trick that you can use to group up widgets together faster is using the SHIFT while clicking on each widget, once creating a group in one of them - the grouping will replicate throughout selected widgets.

### Watchlist and grouping

The watchlist widget has a special property in relation to grouping. Since this widget doesn't have a single symbol but many, users can select the row of their ticker of interest, and widgets that are grouped with the watchlist will get updated accordingly.

<img className="pro-border-gradient" width="800" alt="watchlist" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/d36380df-743a-4676-bec4-6bd34567e661" />

If a user selects a new ticker in another widget that is grouped with the watchlist, that ticker will be added to the watchlist and will become the one selected by default.

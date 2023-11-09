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

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Grouping | OpenBB Terminal Pro Docs" />

The grouping mechanism is extremely powerful as it allows widgets to be grouped together through one of their parameters based on the category they belong to.

For instance, for the equity category, widgets can be connected through their ticker / symbol. Examples are: AAPL to simbolize Apple, TSLA for Tesla and so on.

<img width="1250" alt="276163819-b4c80035-8ead-4fc9-b65b-c5b2c4b8e062" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/435b8fba-e0b7-4aa0-b92f-10d6b12589a2" />

This is an example of 3 widgets that belong to the same group, note the dark yellow 1 on the top right.

In addition, when clicking on the grouping icon you can see that they are grouped around the MSFT ticker.

This means that if a user changes the ticker on any of these widgets, the remaining ones will get updated accordingly.

Also note that the grouping is visible on the sidebar, immediately under the dashboard naming.

<img width="1438" alt="276164492-b773f4ec-6b7d-432a-8e2b-0beb55982857" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/2ccd3148-fec4-4c0b-af30-6f9f5661642c" />


### Watchlist and grouping

The watchlist widget has a special property in relation to grouping. Since this widget doesn't have a single symbol but many, users can select the row of their ticker of interest, and widgets that are grouped with the watchlist will get updated accordingly.

<img width="1227" alt="276165201-9f52500e-5e83-44ba-b5ab-d19c2951a4ea" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/540a1b77-9712-4bfa-802e-f7d4d10c5895" />

If a user selects a new ticker in another widget that is grouped with the watchlist, that ticker will be added to the watchlist and will become the one selected by default.

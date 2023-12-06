---
title: Integrate your own backend
sidebar_position: 2
description: Learn how to integrate your own backend with OpenBB Terminal Pro using
  the cookie-cutter or language-agnostic API approaches, with illustrative guides
  and principles for handling widget.json files, APIs, interfaces, Python, FastAPI
  and more.
keywords:
- OpenBB cookie-cutter
- widgets.json
- OpenBB API
- Endpoint integration
- widget configuration
- Language-Agnostic API
- API implementation
- Python
- FastAPI
- Terminal Pro widgets
- Widget definitions
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Integrate your own backend | OpenBB Terminal Pro Docs" />

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
  youtubeLink="https://www.youtube.com/embed/bkhtgp48MZc?si=kvrq1HgtUIFmhgyX"
  videoLegend="Short introduction to integrating your own backend"
/>

## Using OpenBB Cookie-Cutter

The OpenBB cookie-cutter approach provides a standardized way to host your data and integrate it into widgets. This method is versatile and can be used whether your data is hosted internally or externally. Here's how to get started:

1. **Prepare the `widgets.json` file**: This file defines widget properties such as name, description, category, type, endpoint, and more. Make sure it's well-structured. See an example below.

2. **Set up the OpenBB API**: Follow the OpenBB API documentation to set up your API. Implement the necessary endpoints that align with the widget definitions in the `widgets.json` file.

3. **Integrate endpoints**: Define the appropriate endpoint for each custom widget in the `widgets.json` file. This endpoint connects your API to the widget.

4. **Configure widgets**: Users can add the custom widgets using the Terminal Pro interface by providing the relevant endpoint details.

## Using Language-Agnostic API

The language-agnostic API approach offers flexibility by allowing you to use the programming language and tools that best suit your needs. You can host this API internally or externally, making it accessible to the Terminal Pro widgets. Here's how:

1. **Design and implement your API**: Choose your preferred programming language and framework. Ensure that the API can return data in JSON format, which is required for widget integration.

2. **Create widget definitions**: As with the OpenBB API approach, create corresponding definitions for your custom widgets in the `widgets.json` file. Specify the API endpoint, name, description, category, type, etc.

3. **Connect widgets to your API**: Once your API is up and running, users can add the custom widgets using the Terminal Pro interface. They just need to input the endpoint details, and the widget will fetch and display the data from your API.

### Quick Start with Python and FastAPI

Our team has created several examples that you can use to quickly get started with Python and FastAPI. For more information, check [this open source repository](https://github.com/OpenBB-finance/backend-for-terminal-pro/tree/main) for examples.
e

---
title: Bring your own Copilot
description: Learn how to use your own Copilot with Terminal Pro
keywords:
- OpenBB Copilot
- copilot
- custom
- assistant
- Large language model
- bring your own
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';
import ReactPlayer from 'react-player'

<HeadTitle title="Bring your own Copilot | OpenBB Terminal Pro Docs" />

For scenarios where the default OpenBB Copilot does not meet the specialized
needs of a financial institution, such as when proprietary data and tools are
involved, Terminal Pro offers a solution. Our 'Bring Your Own Copilot' feature
is structured to accommodate the integration of financial firms' custom Large
Language Models (LLMs).

This integration grants the use of Terminal Pro’s full suite of features, while
also capitalizing on the firm's developments in proprietary LLMs. The result is
an enhancement in the efficiency of analysts and researchers, aligning with the
firm's unique data and modeling approaches. Additionally, it ensures that
research queries and data remain within the firm's infrastructure.

## Defining a custom copilot
Incorporating an existing proprietary LLM into Terminal Pro can be achieved by
setting up an API endpoint. This endpoint enables Terminal Pro to interact with
the custom copilot. To facilitate this process, we provide an open-source
Example Copilot that illustrates the necessary steps for integration. 

The example code is available [here](https://github.com/OpenBB-finance/copilot-for-terminal-pro).

## Adding a custom copilot to Terminal Pro

<ReactPlayer width="70%" height="100%" playing loop muted='true' volume='0' url='https://github.com/OpenBB-finance/OpenBBTerminal/assets/14093308/15d2d827-715e-42f3-be62-b3c7f8b26fda' />

After deploying your custom Copilot, you can add it to Terminal Pro.  To do
this, navigate to the "Add copilot" section and follow the prompts:

- Click on the "Add copilot" button.
- Enter the API endpoint of your custom copilot.
- Confirm the addition.
- You are now ready to use your custom copilot. 



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

[![Stargazers][stars-shield]][stars-url]
[![Forks][forks-shield]][forks-url]
[![Contributors][contributors-shield]][contributors-url]
[![MIT License][license-shield]][license-url]

[![Issues][issues-shield]][issues-url]
[![Bugs Open][bugs-open-shield]][bugs-open-url]
[![Bugs Closed][bugs-closed-shield]][bugs-closed-url]

[![Build Status](https://github.com/OpenBB-finance/OpenBBTerminal/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/OpenBB-finance/OpenBBTerminal/actions)
[![Documentation Status](https://readthedocs.org/projects/gamestonk-terminal/badge/?version=latest)](https://gamestonk-terminal.readthedocs.io/?badge=latest)
[![GitHub release](https://img.shields.io/github/release/OpenBB-finance/OpenBBTerminal.svg?maxAge=3600)](https://github.com/OpenBB-finance/OpenBBTerminal/releases)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![TODOs](https://badgen.net/https/api.tickgit.com/badgen/github.com/OpenBB-finance/OpenBBTerminal/main)](https://www.tickgit.com/browse?repo=github.com/OpenBB-finance/OpenBBTerminal&branch=main)

![Discord Shield](https://discordapp.com/api/guilds/831165782750789672/widget.png?style=shield)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/openbb_finance.svg?style=social&label=Follow%20%40openbb_finance)](https://twitter.com/openbb_finance)

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://openbb.co/">
    <img src="images/openbb_gradient.png" alt="Logo" width="1000">
  </a>

  <h3 align="center">OpenBB Terminal 🚀</h3>
  <h4 align="center">Documentation can be found at: https://openbb-finance.github.io/OpenBBTerminal/ </h4>
  <p align="center">Click on the GIF below for a DEMO of the terminal.</p>

<p align="center">
   <a href="https://www.youtube.com/watch?v=fqGPK8OVHLk" rel="OpenBB Terminal Demo">
      <img src="images/openbb_terminal_illustration.gif" alt="OpenBB Terminal Illustration" width="1000"/>
   </a>
</p>

  <p align="center">
    Investment research for everyone.
    <br />
    <a href="https://github.com/OpenBB-finance/OpenBBTerminal/tree/master/openbb_terminal/README.md"><strong>≪  GETTING STARTED</strong></a>
    &nbsp · &nbsp <a href="https://github.com/OpenBB-finance/OpenBBTerminal/tree/master/openbb_terminal/CONTRIBUTING.md"><strong>CONTRIBUTING</strong></a> &nbsp · &nbsp
    <a href="https://openbb-finance.github.io/OpenBBTerminal/">
    <strong>SEE FEATURES »</strong></a>
    <br />
    <br />
    <a href="https://github.com/OpenBB-finance/OpenBBTerminal/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BBug%5D">
    Report Bug</a>
    ·
    <a href="https://github.com/OpenBB-finance/OpenBBTerminal/issues/new?assignees=&labels=enhancement&template=enhancement.md&title=%5BIMPROVE%5D">
    Suggest Improvement</a>
    ·
    <a href="https://github.com/OpenBB-finance/OpenBBTerminal/issues/new?assignees=&labels=new+feature&template=feature_request.md&title=%5BFR%5D">
    Request a Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li> <a href="#about-the-project">About The Project</a> </li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#disclaimer">Disclaimer</a></li>
    <li><a href="#contacts">Contacts</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About The Project

**How it started:**

OpenBB Terminal is an awesome stock and crypto market terminal that has been developed for fun, while I saw my GME
shares tanking. But hey, I like the stock 💎🙌.

**How it's going:**

OpenBB Terminal provides a modern Python-based integrated environment for investment research, that allows
an average joe retail trader to leverage state-of-the-art Data Science and Machine Learning technologies.

As a modern Python-based environment, OpenBBTerminal opens access to numerous Python data libraries in Data Science
(Pandas, Numpy, Scipy, Jupyter), Machine Learning (Pytorch, Tensorflow, Sklearn, Flair), and Data Acquisition
(Beautiful Soup, and numerous third-party APIs).

## Installation

If you wish to install the Terminal, there are currently four options:

- [Using the Installer](https://openbb-finance.github.io/OpenBBTerminal/#accessing-the-openbb-terminal) (recommended if you just want to use the terminal)
- [Using Python](openbb_terminal/README.md#anaconda--python) (recommended if you want to develop new features)
- [Using Docker](openbb_terminal/README.md#Docker-Installation) (alternative option to the installer if preferred)
- [Using Docker Web UI](openbb_terminal/README.md#web-ui---docker) (if you want to deploy the web UI for users to access
  over your LAN)

## Contributing

There are 3 main ways of contributing to this project.

For a 1 hour coding session where the architecture of the repo is explained while a new feature is added, check
[here](https://www.youtube.com/watch?v=9BMI9cleTTg).

**Become a Contributor 🦍**

Recommended if you bought the dip, and the share price keeps dipping. You may as well keep yourself busy while stonks
go up.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Install the pre-commit hooks by running:
   `pre-commit install`.
   Any time you commit a change, linters will be run automatically. On changes, you will have to re-commit.
4. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to your Branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

**Raise an Issue**

Recommended if you adopted a strategy of buying high and selling low.

We are interested in your view on what sort of [features](https://github.com/OpenBB-finance/OpenBBTerminal/issues)
would make you buy even higher and sell even lower.

Also, if somehow you're sitting in several mils due to this terminal, don't forget to report a
[bug](https://github.com/OpenBB-finance/OpenBBTerminal/issues) so that the team can fix, and keep the old ways.

**Join Us and Contribute**

Welcome to the club, and feel free to support the developers behind this amazing open-source project.

If you're interested in contributing, fork us! Grab an issue or enhancement and put in a PR request with the fix.

## License

Distributed under the MIT License. See
[LICENSE](https://github.com/OpenBB-finance/OpenBBTerminal/blob/main/LICENSE) for more information.

## Disclaimer

"A few things I am not. I am not a cat. I am not an institutional investor, nor am I a hedge fund. I do not have
clients and I do not provide personalized investment advice for fees or commissions." DFV

Trading in financial instruments involves high risks including the risk of losing some, or all, of your investment
amount, and may not be suitable for all investors. Before deciding to trade in a financial instrument you should be fully
informed of the risks and costs associated with trading the financial markets, carefully consider your investment
objectives, level of experience, and risk appetite, and seek professional advice where needed. The data contained in GST
is not necessarily accurate. GST and any provider of the data contained in this website will not accept liability for
any loss or damage as a result of your trading, or your reliance on the information displayed.

## Contacts

[Didier Rodrigues Lopes](https://www.linkedin.com/in/didier-lopes/) - dro.lopes@campus.fct.unl.pt

[Artem Veremy](https://www.linkedin.com/in/veremey/) - artem@veremey.net

[James Maslek](https://www.linkedin.com/in/james-maslek-b6810186/) - jmaslek11@gmail.com

Feel free to share loss porn, memes or any questions at:

- Discord: <https://discord.gg/Up2QGbMKHY>
- Twitter: [@openbb_finance](https://twitter.com/openbb_finance)

### Contributors

<a href="https://github.com/OpenBB-finance/OpenBBTerminal/graphs/contributors">
   <img src="https://contributors-img.web.app/image?repo=OpenBB-finance/OpenBBTerminal" height="276"/>
</a>

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=openbb-finance/OpenBBTerminal&type=Date)](https://star-history.com/#openbb-finance/OpenBBTerminal&Date)

## Acknowledgments

- [VICE article - Gamestonk Terminal Is a DIY, Meme Stock Version of Bloomberg Terminal](https://www.vice.com/en/article/qjp9vp/gamestonk-terminal-is-a-diy-meme-stock-version-of-bloomberg-terminal)
- [Daily Fintech article - Never underestimate Bloomberg, but here are 5 reasons why the Gamestonk Terminal is a contender](https://dailyfintech.com/2021/02/25/never-underestimate-bloomberg-but-here-are-5-reasons-why-the-gamestonk-terminal-is-a-contender/)
- [HackerNews - Show HN: Can’t afford Bloomberg Terminal? No prob, I built the next best thing](https://news.ycombinator.com/item?id=26258773)
- [Reddit r/algotrading - Gamestonk Terminal: The next best thing after Bloomberg Terminal.](https://www.reddit.com/r/algotrading/comments/m4uvza/gamestonk_terminal_the_next_best_thing_after/)
- [Reddit r/Python - Gamestonk Terminal: The equivalent to an open-source python Bloomberg Terminal.](https://www.reddit.com/r/Python/comments/m515yk/gamestonk_terminal_the_equivalent_to_an/)
- [Reddit r/Superstonk - Move over Bloomberg Terminal, here comes Gamestonk Terminal](https://www.reddit.com/r/Superstonk/comments/mx2cjh/move_over_bloomberg_terminal_here_comes_gamestonk/)
- [Spotlight: Didier Lopes. Creator of Gamestonk Terminal](https://deepsource.io/spotlight/didier-lopes/)
- [Reddit r/Superstonk - Gamestonk Terminal - We are very much alive](https://www.reddit.com/r/Superstonk/comments/o502i8/gamestonk_terminal_we_are_very_much_alive/)
- [Medium- Gamestonk Terminal. Can't Stop, Won't Stop](https://dro-lopes.medium.com/gamestonk-terminal-cant-stop-won-t-stop-e635662d6f2e)
- [Gamestonk Terminal: UX/UI >> Features](https://dro-lopes.medium.com/gamestonk-terminal-ux-features-f9754b484919)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/OpenBB-finance/OpenBBTerminal.svg?style=for-the-badge
[contributors-url]: https://github.com/OpenBB-finance/OpenBBTerminal/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/OpenBB-finance/OpenBBTerminal.svg?style=for-the-badge
[forks-url]: https://github.com/OpenBB-finance/OpenBBTerminal/network/members
[stars-shield]: https://img.shields.io/github/stars/OpenBB-finance/OpenBBTerminal.svg?style=for-the-badge
[stars-url]: https://github.com/OpenBB-finance/OpenBBTerminal/stargazers
[issues-shield]: https://img.shields.io/github/issues/OpenBB-finance/OpenBBTerminal.svg?style=for-the-badge&color=blue
[issues-url]: https://github.com/OpenBB-finance/OpenBBTerminal/issues
[bugs-open-shield]: https://img.shields.io/github/issues/OpenBB-finance/OpenBBTerminal/bug.svg?style=for-the-badge&color=yellow
[bugs-open-url]: https://github.com/OpenBB-finance/OpenBBTerminal/issues?q=is%3Aissue+label%3Abug+is%3Aopen
[bugs-closed-shield]: https://img.shields.io/github/issues-closed/OpenBB-finance/OpenBBTerminal/bug.svg?style=for-the-badge&color=success
[bugs-closed-url]: https://github.com/OpenBB-finance/OpenBBTerminal/issues?q=is%3Aissue+label%3Abug+is%3Aclosed
[license-shield]: https://img.shields.io/github/license/OpenBB-finance/OpenBBTerminal.svg?style=for-the-badge
[license-url]: https://github.com/OpenBB-finance/OpenBBTerminal/blob/main/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/DidierRLopes

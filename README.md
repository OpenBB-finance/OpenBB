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
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

[![Build Status](https://github.com/DidierRLopes/GamestonkTerminal/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/DidierRLopes/GamestonkTerminal/actions)
[![GitHub release](https://img.shields.io/github/release/DidierRLopes/GamestonkTerminal.svg?maxAge=3600)](https://github.com/DidierRLopes/GamestonkTerminal/releases)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/DidierRLopes/GamestonkTerminal">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Gamestonk Terminal 🚀</h3>

  <p align="center">
    The next best thing after Bloomberg Terminal.
    <br />
    <a href="https://github.com/DidierRLopes/GamestonkTerminal/README.md"><strong>Features »</strong></a>
    <br />
    <br />
    <a href="https://github.com/DidierRLopes/GamestonkTerminal/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BBug%5D">Report Bug</a>
    ·
    <a href="https://github.com/DidierRLopes/GamestonkTerminal/issues/new?assignees=&labels=enhancement&template=enhancement.md&title=%5BIMPROVE%5D">Suggest Improvement</a>
    ·
    <a href="https://github.com/DidierRLopes/GamestonkTerminal/issues/new?assignees=&labels=new+feature&template=feature_request.md&title=%5BFR%5D">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li> <a href="#about-the-project">About The Project</a> </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#install">Install</a></li>
        <li><a href="#advanced-user-install---machine-learning">Advanced User Install - Machine Learning</a></li>
        <li><a href="#api-keys">API Keys</a></li>
        <li><a href="#usage">Usage</a></li>
      </ul>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#disclaimer">Disclaimer</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About The Project

How it started:
"Gamestonk Terminal is an awesome stock and crypto market terminal that has been developed for fun, while I saw my GME shares tanking. But hey, I like the stock 💎🙌."

How it's going:
u/schoen: _(...) I think people have upvoted this so much because it's an initial version of a single person's passion project that manages to put a whole bunch of financial information at your fingertips. With an active community, it could easily grow and grow and grow in functionality._


## Getting Started
### Install

This project was originally written and tested with Python 3.6.8. It should now support Python 3.6, 3.7, and 3.8.

Our current recommendation is to use this project with Anaconda's Python distribution - either full [__Anaconda3 Latest__](https://repo.anaconda.com/archive/) or [__Miniconda3 Latest__](https://repo.anaconda.com/archive/). Several features in this project utilize Machine Learning. Machine Learning Python dependencies are optional. If you decided to add Machine Learning features at a later point, you will likely have better user experience with Anaconda's Python distribution.

1. Install [Anaconda](https://docs.anaconda.com/anaconda/install/)

Confirm that you have it with: `conda -V`

The output should be like `conda 4.9.2`

2. Create Environment

You can name the environment whatever you want. Although you could use names such as: `welikethestock`, `thisistheway` or `diamondhands`, we recommend something simple and intuitive like `gst`. This is because this name will be used from now onwards.
```
conda create -n gst python=3.6.8
````

3. Activate the virtual environment

```
conda activate gst
```
Note: At the end, you can deactivate it with `conda deactivate`

4. Fork the Project

- Via HTTPS: `git clone https://github.com/DidierRLopes/GamestonkTerminal.git`
- via SSH:  `git clone git@github.com:DidierRLopes/GamestonkTerminal.git`

Navigate into the folder with `cd GamestonkTerminal/`

5. Install poetry
```
conda install poetry
```

6. Install poetry dependencies
```
poetry install
```
This is a library for package management, and makes sure to should ensure a better experience than: ``pip install -r requirements.txt``

7.  You're ready to Gamestonk it!

```
python terminal.py
```

### Advanced User Install - Machine Learning

If you are an advanced user and use other Python distributions, we have several requirements.txt documents that you can pick from to download project dependencies.

Note: The libraries specified in the [requirements.txt](/requirements.txt) file have been tested and work for the purpose of this project, however, these may be older versions. Hence, it is recommended for the user to set up a virtual python environment prior to installing these. This allows to keep dependencies required by different projects in separate places.

*If you would like to use optional Machine Learning features:*

* Update your *gamestonk_terminal/config_terminal.py*
```
ENABLE_PREDICT = False
```

* Install optional *prediction* dependency collection with poetry
```
poetry install -E prediction
```

*If you would like to set up a docker image:*

* Build the docker: `docker build .`
* Run it: `docker run -it gamestonkterminal:dev `

Note: The problem with docker is that it won't output matplotlib figures.

*Commands that may help you in case of an error:*
* `conda install -c conda-forge fbprophet -y`
* `python -m pip install --upgrade pip`
* `pip install pystan --upgrade`

### API Keys

The project is build around several different API calls, whether it is to access historical data or financials.

These are the ones where a key is necessary:
  * Alpha Vantage: https://www.alphavantage.co
  * Financial Modeling Prep: https://financialmodelingprep.com/developer
  * Quandl: https://www.quandl.com/tools/api
  * Reddit: https://www.reddit.com/prefs/apps
  * Twitter: https://developer.twitter.com

When these are obtained, don't forget to update [config_terminal.py](/config_terminal.py).  Alternatively, you can also set them to the following environment variables:
  * GT_API_KEY_ALPHAVANTAGE
  * GT_API_KEY_FINANCIALMODELINGPREP
  * GT_API_KEY_QUANDL
  * GT_API_REDDIT_CLIENT_ID
  * GT_API_REDDIT_CLIENT_SECRET
  * GT_API_REDDIT_USERNAME
  * GT_API_REDDIT_USER_AGENT
  * GT_API_REDDIT_PASSWORD
  * GT_API_TWITTER_KEY
  * GT_API_TWITTER_SECRET_KEY
  * GT_API_TWITTER_BEARER_TOKEN.

Note that it is not necessary to have a valid Alpha Vantage key to get daily OHLC values.

### Usage

Start by loading a ticker of interest:
```
load -t GME
```
The menu will expand to all its menus since a ticker has been loaded.

View the historical data of this stock:
```
view
```
Apply some technical indicators to the ticker, starting at 2020-06-04.
Re-load ticker with starting time, this time:
```
load -t GME -s 2020-06-04
```
Enter in technical analysis menu with
```
ta
```
and run a SMA with:
```
sma
```
However, imagine that you wanted to change the length of the window because you don't want to go long but do a swing, and therefore a smaller window is necessary. Check what settings are available on the SMA command:
```
sma -h
```
Once that has been seen, set the parameters that you want after flagging them. In this case, to change length window to 10, we would have to do:
```
sma -l 10
```

<!-- CONTRIBUTING -->
## Contributing

There are 3 main ways of contributing to this project.

**Become a Contributor 🦍**

Recommended if you bought the dip, and the share price keeps dipping. You may as well keep yourself busy while stonks go up.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to your Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


**Become a Karen 🤷**

Recommended if you adopted a strategy of buying high and selling low.

We are interested in your view on what sort of [features](https://github.com/DidierRLopes/GamestonkTerminal/issues) would make you buy even higher and selling even lower.

Also, if somehow you're sitting in several mils due to this terminal, don't forget to report a [bug](https://github.com/DidierRLopes/GamestonkTerminal/issues) so that the team can fix, and keep the old ways.


**Join the 🙌 💎 Gang**

If red is your favourite color, and you never sell for a loss.

Welcome to the club, and feel free to support the developers behind this amazing open-source project.

<a href="https://www.buymeacoffee.com/didierlopes" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-yellow.png" alt="Buy Me A Coffee" height="41" width="174"></a>


## License

Distributed under the MIT License. See [LICENSE](https://github.com/DidierRLopes/GamestonkTerminal/blob/main/LICENSE) for more information.

## Disclaimer
"A few things I am not. I am not a cat. I am not an institutional investor, nor am I a hedge fund. I do not have clients and I do not provide personalized investment advice for fees or commissions." DFV

## Contact

[Didier Rodrigues Lopes](https://www.linkedin.com/in/didier-lopes/) - dro.lopes@campus.fct.unl.pt

## Acknowledgments

* [VICE article](https://www.vice.com/en/article/qjp9vp/gamestonk-terminal-is-a-diy-meme-stock-version-of-bloomberg-terminal)
* [Daily Fintech article](https://dailyfintech.com/2021/02/25/never-underestimate-bloomberg-but-here-are-5-reasons-why-the-gamestonk-terminal-is-a-contender/)
* [HackerNews](https://news.ycombinator.com/item?id=26258773)
* [Reddit](https://www.reddit.com/r/algotrading/comments/lrndzi/cant_afford_the_bloomberg_terminal_no_worries_i/)


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/DidierRLopes/repo.svg?style=for-the-badge
[contributors-url]: https://github.com/DidierRLopes/repo/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/DidierRLopes/repo.svg?style=for-the-badge
[forks-url]: https://github.com/DidierRLopes/repo/network/members
[stars-shield]: https://img.shields.io/github/stars/DidierRLopes/repo.svg?style=for-the-badge
[stars-url]: https://github.com/DidierRLopes/repo/stargazers
[issues-shield]: https://img.shields.io/github/issues/DidierRLopes/repo.svg?style=for-the-badge
[issues-url]: https://github.com/DidierRLopes/repo/issues
[license-shield]: https://img.shields.io/github/license/DidierRLopes/repo.svg?style=for-the-badge
[license-url]: https://github.com/DidierRLopes/repo/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/DidierRLopes

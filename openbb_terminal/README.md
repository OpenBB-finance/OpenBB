# OpenBB Terminal

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
    <ol>
      <li><a href="#anaconda--python">Anaconda & Python Installation</a></li>
      <li><a href="#docker-installation">Docker Installation</a></li>
      <li><a href="#api-keys">API Keys</a></li>
    </ol>
</details>

---

There are currently four options to install the terminal:

- [Using the Installer](https://openbb-finance.github.io/OpenBBTerminal/#accessing-the-openbb-terminal) (recommended if you just want to use the terminal)
- [Using Python](#anaconda--python) (recommended if you want to develop new features)
- [Using Docker](#docker-installation) (alternative option to the installer if preferred)

First step in all options is to star the project

<img width="1512" alt="OpenBB Terminal GitHub Stars" src="https://user-images.githubusercontent.com/46355364/176408138-771ec9ae-c873-4406-b964-939b8e433c15.png">

## Anaconda & Python

This installation type supports both Windows and Unix systems (Linux + MacOS).

**NOTE for Windows users:** Some _not all_ Windows users would prefer to use an environment
similar to what Linux and macOS users use. In this case it is easier to use Windows Subsystem
for Linux (WSL). WSL emulates a Linux machine inside your Windows system. If this is the case -
jump to the <a href="#installing-wsl-only-for-windows-users)">Installing WSL (Only for Windows users)</a>
section before proceeding.

### Installing the terminal

These steps are common in all operating systems (Windows with or without WSL, MacOS or Linux).

This project supports Python 3.8 and 3.9. By default, the newly created virtual environment will use Python 3.9.13

Our current recommendation is to use this project with Anaconda's Python distribution - either full
[**Anaconda3 Latest**](https://www.anaconda.com/products/distribution) or
[**Miniconda3 Latest**](https://docs.conda.io/en/latest/miniconda.html) (recommended).
Several features in this project utilize Machine Learning. Machine Learning Python dependencies are optional. For MacOS systems, the "Miniconda3 MacOSX 64-bit" version that works on both Intel and M1
macs is recommended.

**NOTE:** We recommend using `conda` and `poetry` because it just works. You can use other python
distributions and use raw `pip` instead of `poetry` but you will very likely bump into installation
issues.

#### 1. [Install Miniconda](https://docs.conda.io/en/latest/miniconda.html)

Miniconda is a python environment and package manager. It is required if you want to
have the dependencies working straight away.

- Follow the [link to the page with the latest installers for all platforms](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links) or click direct links to installer packages based on your operating system:
   - If you are using macOS click [Miniconda for MacOS](https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh)
   - If you are using WSL or Linux click [Miniconda for Linux](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh)
   - If you are using a Raspberry PI click [Miniconda for Raspberry PI](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh)
   - If you are using Windows click [Miniconda for Windows](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe).

      **ONLY REQUIRED ON WINDOWS IF NOT USING WSL**, Install/update Microsoft C++ Build Tools from here: <https://visualstudio.microsoft.com/visual-cpp-build-tools/>

   **NOTE for macOS users:** The link above gets you the Intel version of miniconda meaning if you're on an
   Apple Silicon powered machine you will be using the terminal through Apple's rosetta2 layer. We recommend
   sticking to this distribution for better compatibility until the dependency developers fully catch up with
   Apple's transition to Apple Silicon.

- After following the steps, confirm that you have it by opening a terminal and running: `conda -V`. The output should be something along the lines of: `conda 22.9.0`

#### 2. Install CMake

CMake is required by several python modules.

**On Linux or Raspberry Pi:**

```bash
sudo apt update
sudo apt install -y gcc cmake
```

**On macOS**

Check if you have homebrew installed by running `brew --version`

If you don't have homebrew installed run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install cmake
```

If you have homebrew installed run:

```bash
brew install cmake
```

**On Windows**

If you have followed the instructions in step 1 of this guide CMake was installed as a
part of you Microsoft C++ Build Tools

#### 3. Install git

```bash
conda install -c anaconda git
```

#### 4. Clone the Project

- Via HTTPS: `git clone https://github.com/OpenBB-finance/OpenBBTerminal.git`
- via SSH: `git clone git@github.com:OpenBB-finance/OpenBBTerminal.git`

#### 5. Navigate into the project's folder

```bash
cd OpenBBTerminal/
```

#### 6. Create Environment

You can name the environment whatever you want. Although you could use names such as:
`welikethestock`, `thisistheway` or `diamondhands`, we recommend something simple and
intuitive like `obb`. This is because this name will be used from now onwards.

Please note, the following setup has been confirmed to work for all OS (including M1)
with the standard miniconda distribution. If you are using a different distribution,
you will need to install it manually before proceeding.

```bash
conda env create -n obb --file build/conda/conda-3-9-env.yaml
```

Or, to include machine learning type:

```bash
conda env create -n obb --file build/conda/conda-3-9-env-full.yaml
```

Note: Using python 3.10+ can lead to undesirable functionality for certain commands.

#### 7. Activate the virtual environment

```bash
conda activate obb
```

Note: At the end, you can deactivate it with: `conda deactivate`.

#### 8. Install dependencies with poetry

Install the main dependencies with

```bash
poetry install
```

You are good to go with the core of the OpenBB Terminal. To install additional toolkits
proceed with the following commands:

To install the Portfolio Optimization Toolkit run:

```bash
poetry install -E optimization
```

To install the Machine Learning Toolkit run:

```bash
poetry install -E prediction
```

#### 9. You're ready to use the terminal!

```bash
openbb
```

Or if you are old-fashioned run:

```bash
python terminal.py
```

**NOTE:** When you close the terminal and re-open it, the only command you need to re-call
is `conda activate obb` before you call `openbb` again.

**TROUBLESHOOT:** If you are having troubles to install, check out the
[troubleshoot page](https://github.com/OpenBB-finance/OpenBBTerminal/blob/master/TROUBLESHOOT.md).

You can also reach for help on our [discord](https://discord.gg/Up2QGbMKHY).

## Advanced User Install - Custom installation procedures

By default we advice using `conda` and `poetry` for environment setup and dependency management.
Conda ships binaries for packages like `numpy` so these dependencies are not built from source locally by `pip`.
Poetry solves the dependency tree in a way that the dependencies of dependencies of dependencies
use versions that are compatible with each other.

If you are using a conda environment the `build/conda` folder contains multiple `.yaml` configuration
files that you can choose from.

If you are using other python distributions we highly recommend that you use some virtual
environment like `virtualenv` or `pyenv` for installing the terminal dependency libraries.

Requirements files that you can find in the project root:

- `requirements.txt` list all the dependencies without Machine Learning libraries
- `requirements-full.txt` list all the dependencies without Machine Learning libraries

You can install them with with pip

 ```bash
 pip install -r requirements.txt
 ```

The dependency tree is solved by poetry.

Note: The libraries specified in the requirements files have been tested and work for
the purpose of this project, however, these may be older versions. Hence, it is recommended
for the user to set up a virtual python environment prior to installing these. This allows
to keep dependencies required by different projects in separate places.

### Installing WSL (Only for Windows users)

If you are using Windows you first you need to install WSL. The process is simple and a tutorial can be found [here](https://www.sitepoint.com/wsl2/).
Once you reach the section **Update Linux** on that tutorial, you should have a linux machine installed and can proceed
to the next steps.

Since WSL installation is headless by default (i.e., you have only access to a terminal running a linux distribution)
you need some extra steps to be able to visualize the charts produced by the terminal (more detailed tutorial [here](https://medium.com/@shaoyenyu/make-matplotlib-works-correctly-with-x-server-in-wsl2-9d9928b4e36a)):

1. Dynamically export the DISPLAY environment variable in WSL2:

   ```bash
   # add to the end of ~/.bashrc file
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
   # source the file
   source ~/.bashrc
   ```

2. Download and install [VcXsrv](https://sourceforge.net/projects/vcxsrv/)
3. When running the program is important to check "Disable access control"

After this, `VcXsrv` should be running successfully and we can proceed to terminal installation.

## Update Terminal

The terminal is constantly being updated with new features and bug fixes, hence, for your terminal to be update,
you can run:

```bash
git pull
```

to get the latest changes.

If this fails due to the fact that you had modified some python files, and there's a conflict with the updates, you can use:

```bash
git stash
```

Then, re-run `poetry install` to get any new dependencies.

Once installation is finished, you're ready to openbb.

If you `stashed` your changes previously, you can un-stash them with:

```bash
git stash pop
```

**NOTE:** When you close the terminal and re-open it, the only command you need to re-call is `conda activate gst`
before you call `openbb` again.

### API Keys

The project is build around several different API calls, whether it is to access historical data or financials.
The table below shows the ones where a key is necessary. The easiest way is of updating the keys is by using the
terminal, see [this guide](https://openbb-finance.github.io/OpenBBTerminal/terminal/#accessing-other-sources-of-data-via-api-keys).

You can also use the environment variable to set your API Keys directly instead of using the Terminal, for the variable
name in the code one just needs to remove the "GT\_", this can be found in [config_terminal.py](/openbb_terminal/config_terminal.py).

| Website | Environment Variables |
| :------ | :-------------------- |
| [Alpha Vantage](https://www.alphavantage.co) | OPENBB_API_KEY_ALPHAVANTAGE |
| [Binance](https://binance.com) | OPENBB_API_BINANCE_KEY <br/> OPENBB_API_BINANCE_SECRET |
| [BitQuery](https://bitquery.io/pricing) | OPENBB_API_BITQUERY_KEY |
| [Coinbase](https://docs.pro.coinbase.com/) | OPENBB_API_COINBASE_KEY <br/> OPENBB_API_COINBASE_SECRET <br/> OPENBB_API_COINBASE_PASS_PHRASE |
| [Coinglass](https://coinglass.github.io/API-Reference/#api-key) | OPENBB_API_COINGLASS_KEY |
| [CoinMarketCap](https://coinmarketcap.com) | OPENBB_API_CMC_KEY <br/> |
| [Cryptopanic](https://cryptopanic.com/developers/api/) | OPENBB_API_CRYPTO_PANIC_KEY |
| [DEGIRO](https://www.degiro.fr) | OPENBB_DG_USERNAME <br/> OPENBB_DG_PASSWORD <br/> OPENBB_DG_TOTP_SECRET |
| [Ethplorer](https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API) | OPENBB_API_ETHPLORER_KEY |
| [Financial Modeling Prep](https://financialmodelingprep.com) | OPENBB_API_KEY_FINANCIALMODELINGPREP |
| [Finnhub](https://finnhub.io) | OPENBB_API_FINNHUB_KEY |
| [FRED](https://fred.stlouisfed.org) | OPENBB_API_FRED_KEY |
| [GitHub](https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api) | OPENBB_API_GITHUB_KEY |
| [Glassnode](https://docs.glassnode.com/basic-api/api-key#how-to-get-an-api-key) | OPENBB_API_GLASSNODE_KEY |
| [News](https://newsapi.org) | OPENBB_API_NEWS_TOKEN |
| [Oanda](https://developer.oanda.com) | OPENBB_OANDA_TOKEN <br/> OPENBB_OANDA_ACCOUNT |
| [Polygon](https://polygon.io) | OPENBB_API_POLYGON_KEY |
| [Quandl](https://www.quandl.com) | OPENBB_API_KEY_QUANDL |
| [Reddit](https://www.reddit.com) | OPENBB_API_REDDIT_CLIENT_ID <br> OPENBB_API_REDDIT_CLIENT_SECRET <br/> OPENBB_API_REDDIT_USERNAME <br/> OPENBB_API_REDDIT_USER_AGENT <br/> OPENBB_API_REDDIT_PASSWORD |
| [SentimentInvestor](https://sentimentinvestor.com) | OPENBB_API_SENTIMENTINVESTOR_TOKEN <br> OPENBB_API_SENTIMENTINVESTOR_KEY |
| [Tradier](https://developer.tradier.com) | OPENBB_TRADIER_TOKEN |
| [Twitter](https://developer.twitter.com) | OPENBB_API_TWITTER_KEY <br/> OPENBB_API_TWITTER_SECRET_KEY <br/> OPENBB_API_TWITTER_BEARER_TOKEN |
| [Whale Alert](https://docs.whale-alert.io/) | OPENBB_API_WHALE_ALERT_KEY |

Example:

```bash
export OPENBB_API_REDDIT_USERNAME=SexyYear
```

Environment variables can also be set in a `.env` file at the top of the repo. This file is ignored by git so your API
keys will stay secret. The above example stored in `.env` would be:

```bash
OPENBB_API_REDDIT_USERNAME=SexyYear
```

Note that the `OPENBB_API_REDDIT_USER_AGENT` is the name of the script that you set when obtained the Reddit API key.
Note that it is not necessary to have a valid Alpha Vantage key to get daily OHLC values.

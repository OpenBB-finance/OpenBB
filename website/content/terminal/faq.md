---
title: FAQ
sidebar_position: 5
keywords: [faq, questions, openbb, terminal, troubleshooting, errors, bugs, issues, problems, installation, contributors, developers, github, pip]
---
Still experiencing trouble after consulting this page? Reach us on [Discord](https://openbb.co/discord) or visit our [contact page](https://openbb.co/contact).

## Installation and Updates

<details><summary>How much hard drive space is required?</summary>

An installation will use approximately 4GB of space.

</details>

<details><summary>What is the minimum version of Windows or MacOS required to install the OpenBB Terminal?</summary>

The OpenBB Terminal installation packages are compatible with:

- Windows 10 or later.
- MacOS Monterey or later.

**Note:** Machines which are not compatible with the installer packages may be able to install from the source code.

</details>

<details><summary>How do I update my installation to the latest version?</summary>

The terminal is constantly being updated with new features and bug fixes. The process for updating will vary by the installation type:

- As of version 2.4.1, the Windows installer has an option for uninstalling the existing prior to updating.
- For other installer versions, uninstall the previous version (uninstall.exe for Windows, delete the Application folder on MacOS); then, download the latest version and reinstall. User settings and data will remain.
- For a `pip` installation, when a new version is published: `pip install -U openbb[all]`
- Upgrade a cloned version of the GitHub repo with:

```console
git fetch
git pull
poetry install -E all
```

**Notes:** If the cloned repository is a fork, pull from: `git pull origin main` or `git pull origin develop`. If there are changes locally to the files that conflict with the incoming changes from GitHub, stash them before pulling from main with `git stash`.

</details>

<details><summary>"Microsoft Visual C++ 14.0 or greater is required"</summary>

Download and install [C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/), restart the machine, then try again.

</details>

<details><summary>Error: failed building wheel for bt</summary>

There may be an additional message that is printed from this error, stating: "Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools".

Download and install it. [https://visualstudio.microsoft.com/visual-cpp-build-tools/](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

Mac and Linux users may also encounter a similar error because a C++ compiler is not installed. Install Homebrew:

```console
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then run:

```console
brew install gcc
brew install cmake
```

</details>

<details><summary>Miniconda3 will not install on ARM/Linux Raspberry Pi machines.</summary>

Refer to this issue on the Conda [GitHub](https://github.com/conda/conda/issues/10723) page.

</details>

## Launching

<details><summary>Mac: Invalid CPU Type - Terminal fails to launch.</summary>

This error is usually the result of a Mac M1/M2 machine which does not have Rosetta installed. Install from the system Terminal command line:

```console
softwareupdate --install-rosetta
```

</details>

<details><summary>Terminal app does not launch: Failed to execute script 'terminal' due to unhandled exception!</summary>

When an installer-packaged version of the OpenBB Terminal fails to launch, because of this message, the machine may have an obsolete CPU-type or operating system. Please try installing via the source code, and if problems persist, reach out to us on [Discord](https://discord.gg/xPHTuHCmuV) or fill out a support request form on our [website](https://openbb.co/support).

</details>

<details><summary>ModuleNotFoundError: No module named '______'</summary>

Before troubleshooting please verify that the recommended installation instructions were followed. These errors often can occur when the virtual environment has not been activated, or the `poetry install` command was skipped. Activate the OpenBB virtual environment created during the installation process prior to launching or importing the SDK.

**Terminal**:

```console
conda activate obb
python terminal.py
```

**SDK**:

```console
conda activate obb
ipython
from openbb_terminal.sdk import openbb
```

**Jupyter**:

Check that the kernel selected for the session is the OpenBB virtual environment created during the installation process and then re-run the cell.

```console
from openbb_terminal.sdk import openbb
```

There is also a possibility that a new dependency has been added to the code and it has not yet been installed in the environment. This may happen after updating the code from GitHub, but before running the `poetry install` install command.

```console
poetry install -E all
```

</details>

<details><summary>Fontconfig warning: ignoring UTF-8: not a valid region tag</summary>

In the OS default terminal shell profile, check for a variable similar to, “set locale environment variables at startup”, then also, set text encoding to UTF-8.

</details>

<details><summary>SSL certificates fail to authorize</summary>

```console
SSL: CERTIFICATE_VERIFY_FAILED
```

An error message, similar to above, is usually encountered while attempting to use the OpenBB Platform from behind a firewall.  A workplace environment is typically the most common occurrence.  Try connecting to the internet directly through a home network to test the connection. If using a work computer and/or network,  we recommend speaking with the company's IT department prior to installing or running any software.

A potential solution is to try:

```console
pip install pip-system-certs
```

</details>

<details><summary>Cannot connect due to proxy connection.</summary>

Find the `.env` file (located at the root of the user account folder: (`~/.openbb_terminal/.env`), and add a line at the bottom of the file with:

```console
HTTP_PROXY="<ADDRESS>" or HTTPS_PROXY="<ADDRESS>”
```

</details>

<details><summary> Linux Ubuntu installation was successful but now hangs on launch.</summary>

Check that VcXsvr - or an equivalent X-host - is running and configured prior to launch.

</details>

## General Operation

<details><summary>Charts do not display on Linux/WSL or Docker installation.</summary>

Check that X-11, or similar, is installed, open, and configured. Follow the instructions pertaining to the system here: [https://docs.openbb.co/terminal/quickstart/installation#3-configuring-your-x-server-to-show-plots](https://docs.openbb.co/terminal/quickstart/installation#3-configuring-your-x-server-to-show-plots)

</details>

<details><summary>How do I retrieve more results than is returned by default?</summary>

Most functions will have either, `--start` and `--end` flags, or a `--limit` argument. Print the help dialogue for any command by attaching, `--help` or `-h`.

</details>

<details><summary>Does the portfolio menu allow for dividends, interest, or other distributions?</summary>

Currently, this is only possible by manually updating the portfolio file.

</details>

<details><summary>Why does my Portfolio file fail to load?</summary>

This can be the result of a formatting error, check the file in a simple text editor to observe any abnormalities in the formatting; or, it could be a bug - check the [GitHub issues page](https://github.com/OpenBB-finance/OpenBBTerminal/issues) for similar errors.

- Check that all the necessary column titles are present.
- Inspect the file to see if cells left blank have been filled unintentionally with 0 or NaN values.
- A particular asset may not be able to load data. Check for valid historical data from the Stocks menu.
- Format ticker symbols according to yFinance naming convention.
- All dates must be entered as YYYY-MM-DD.
- Transactions dated for today will fail to load historical data.
- MacOS users should attempt to avoid using the Numbers application as it has a habit of changing the formatting while saving.

Files can be formatted as either `.csv` or `.xlsx` files, and the required column headers are:

`[Date,Type,Ticker,Side,Price,Quantity,Fees,Investment,Currency,Sector,Industry,Country,Region]`

See the guide [here](https://docs.openbb.co/sdk/guides/intros/portfolio) for more information.

</details>

<details><summary>How do I change the chart styles?</summary>

Place style sheets in this folder: `OpenBBUserData/styles/user`

SDK users can refer to the documentation [here](https://docs.openbb.co/sdk/guides/advanced/chart-styling) for syntax. A sample Matplotlib configuration file can be copied from [here](https://matplotlib.org/stable/tutorials/introductory/customizing.html#the-default-matplotlibrc-file).

</details>

<details><summary>Can I change the colors of the text in the Terminal?</summary>

Yes, follow the directions on this page: [https://openbb.co/products/terminal?customizeMenu=true#terminal](https://openbb.co/products/terminal?customizeMenu=true#terminal)

</details>

<details><summary>After setting the preset in the stocks screener, nothing happens.</summary>

Print the current screen again with by entering, `?`. Does the name of the selected preset display? With a preset loaded, run the screener by entering one of the commands below:

- Financial
- Ownership
- Overview
- Performance
- Technical
- Valuation

</details>

<details><summary>Forecast functions say to enter a valid data set</summary>

Because an unlimited number of data sets can be loaded into the Forecast menu, each function requires defining the specific data set to be used. Add the `-d` or `--dataset` argument to the command, along with the name of the desired data set.

```console
rnn -d SPY
```

</details>

## Data and Sources

Please note that OpenBB does not provide any data, it is an aggregator which provides users access to data from a variety of sources. OpenBB does not maintain or have any control over the raw data supplied. If there is a specific problem with the output from a data provider, please consider contacting them first.

<details><summary>Data from today is missing.</summary>

By default, the load function requests end-of-day daily data and is not included until the EOD summary has been published. The current day's data is considered intraday and is loaded when the `interval` argument is present.

```console
load SPY -i 60
```

</details>

<details><summary>Can I stream live prices and news feeds?</summary>

The OpenBB Terminal is not currently capable of streaming live feeds through websocket connections.

</details>

<details><summary>"Pair BTC/USDT not found in binance"</summary>

US-based users are currently unable to access the Binance API. Please try loading the pair from a different source, for example:

`load btc --source CCXT --exchange kraken`

</details>

## General Troubleshooting

Both Windows and MacOS provide a "developer mode", and enabling it may help.

**MacOS**: Go to the System Settings, and under the "Privacy and Security" tab, scroll to the bottom and select the option to "Allow applications downloaded from App Store and identified developers". Then, scroll up to click on, "Developer Tools", and add `Terminal.app` and `Visual Studio Code` (or the preferred code editor) to the list of applications allowed to run software locally that does not meet the system's security policy.

**Windows**: Go to the Control Panel, and under the "Privacy & Security" tab, click on, "For developers". Under this menu, turn "Developer Mode" on.

From the Windows Security menu, click on the Firewall & Network Protection tab, then click on "Allow an app through firewall". If the applications below are not allowed to communicate through Windows Defender Firewall, change the settings to allow.

- BranchCache
- Hyper-V
- VcXsrv
- Windows Terminal

<details><summary>Why does a specific menu or command not exist?</summary>

It could be that you are running an outdated version in which the menu or command is not yet available. Please check the [installation guide](https://docs.openbb.co/terminal/quickstart/installation) to download the most recent release.

Do note that it is also possible that the menu or command has been deprecated. If this is oversight, please reach out to us [here](https://openbb.co/support).

</details>

## Bugs, Support, and Feedback

When an error is encountered, it is always a good idea to check the open issues on [GitHub](https://github.com/OpenBB-finance/OpenBBTerminal/issues). There may be a workaround solution for the specific problem until a patch is released.

<details><summary>How often are patches for bugs released?</summary>

The installer versions are packaged approximately every two-weeks. Those working with a cloned GitHub version can checkout the Develop branch to get the latest fixes and releases before they are pushed to the main branch.

```console
git checkout develop
```

</details>

<details><summary>How do I report a bug?</summary>

First, search the open issues for another report. If one already exists, attach any relevant information and screenshots as a comment. If one does not exist, start one with this [link](https://github.com/OpenBB-finance/OpenBBTerminal/issues/new?assignees=&labels=type%3Abug&template=bug_report.md&title=%5BBug%5D)

</details>

<details><summary>How can I get help with OpenBB Terminal?</summary>

You can get help with OpenBB Terminal by joining our [Discord server](https://openbb.co/discord) or contact us in our support form [here](https://openbb.co/support).

</details>

<details><summary>How can I give feedback about the OpenBB Terminal, or request specific functionality?</summary>

Being an open source platform that wishes to tailor to the needs of any type of investor, we highly encourage anyone to share with us their experience and/or how we can further improve the OpenBB Terminal. This can be anything from a very small bug, a new feature, or the implementation of a highly advanced Machine Learning model.

You are able to directly send us information about a bug or a question/suggestion from inside the terminal by using the `support` command which is available everywhere in the terminal. Here you can select which command you want to report a bug on, ask a question or make a suggestion. After entering `support`, when you press `ENTER` (⏎), you are taken to the Support form which is automatically filled with your input. You are only required to include the type (e.g. bug, suggestion or question) and message in the form, although this can also be set directly from inside the terminal (see `support -h`).

Alternatively, you can contact us via the following routes:

- If you notice that a feature is missing inside the terminal, please fill in the [Request a Feature](https://openbb.co/request-a-feature) form.
- If you wish to report a bug, have a question/suggestion or anything else, please fill in the [Support](https://openbb.co/support) form.
- If you wish to speak to us directly, please contact us on [Discord](https://openbb.co/discord).

</details>

## Developer Issues

<details><summary>Error: "git pull" fails because of a hot fix: cannot lock ref</summary>

If the error message looks something like:

```console
cannot lock ref: 'refs/remotes/origin/hotfix' exists; cannot create
```

Try:

```console
git remote prune origin
git pull
```

</details>

<details><summary>What does it mean if it says wheel is missing?</summary>

If you receive any notifications regarding `wheel` missing, this could be due to this dependency missing.

`conda install -c conda-forge wheel` or `pip install wheel`

</details>

<details><summary>Why do these .whl files not exist?</summary>

If you get errors about .whl files not existing (usually on Windows) you have to reinitialize the following folder.
Just removing the 'artifacts' folder could also be enough:

| Platform | Location                        |
| -------- | ------------------------------- |
| Linux    | "~/.cache/pypoetry"             |
| Mac      | "~/Library/Caches/pypoetry"     |
| Windows  | "%localappdata%/pypoetry/cache" |

When you try to add a package to Poetry it is possible that it causes a similar issue. Here you can remove the
'artifacts' folder again to reinitialize Poetry.

If you run into trouble with Poetry, and the advice above did not help, your best bet is to try

- `poetry update --lock`
- `conda deactivate` -> `conda activate obb`, then try again
- Track down the offensive package and purge it from your anaconda `<environment_name>` folder, then try again

| Platform  | Location                                    |
| --------- | ------------------------------------------- |
| Linux/Mac | ~/anaconda3/envs, or , ~/opt/anaconda3/envs |
| Windows   | %userprofile%/anaconda3/envs                |

- Completely nuke your conda environment folder and make a new environment from scratch

  - `conda deactivate`
  - `conda env remove -n obb`
  - `conda clean -a`
  - Make a new environment and install dependencies again.
- Reboot your computer and try again
- Submit a ticket on GitHub

</details>

<details><summary>What does the JSONDecodeError mean during poetry install?</summary>

Sometimes poetry can throw a `JSONDecodeError` on random packages while running `poetry install`. This can be observed on macOS 10.14+ running python 3.8+. This is because of the use of an experimental installer that can be switched off to avoid the mentioned error. Run the code below as advised [here](https://github.com/python-poetry/poetry/issues/4210) and it should fix the installation process.

```bash
poetry config experimental.new-installer false
```

_Commands that may help you in case of an error:_

- `python -m pip install --upgrade pip`
- `poetry update --lock`
- `poetry install`

</details>

<details><summary>How do I deal with errors regarding CRLF?</summary>

When trying to commit code changes, pylint will prevent you from doing so if your line break settings are set to
CRLF (default for Windows).
This is because the entire package uses LF (default for Linux/Mac), and it is therefore
important that you change this setting to LF _before_ you make any changes to the code.

It is possible that CRLF automatically turns back on, you can correct this with:

```bash
git config --global core.autocrlf false
```

In case you already made coding adjustments, you have to reset your cache, and the changes you made to the code with
the following:

```bash
git rm --cached -r .
git reset --hard
```

</details>

<details><summary>Why can't I run OpenBB via the VS Code integrated terminal?</summary>

This occurs when VS Code terminal python version/path is different from the terminal version.

To fix it add this to vscode JSON settings ([ref](https://stackoverflow.com/questions/54582361/vscode-terminal-shows-incorrect-python-version-and-path-launching-terminal-from)):

```bash
    "terminal.integrated.inheritEnv": false,
```

</details>

---
title: FAQ
sidebar_position: 3
---

## General

<details><summary>Where does the data from the OpenBB Terminal come from?</summary>
<p>

The OpenBB platform does not provide any data itself as the platform is a data aggregator that connects to
almost a hundred different data providers and APIs to access the data.

</p>
</details>

<details><summary>What programs need to be allowed for Windows Firewall?</summary>
<p>

When issues arise regarding Windows Firewall, please allow the following applications through (if not already):

- BranchCache
- Hyper-V
- VcXsrv
- Windows Terminal

From the Windows Security menu, click on the Firewall & Network Protection tab, then click on "Allow an app through firewall". If the applications below are not allowed to communicate through Windows Defender Firewall, change the settings to allow.

</p>
</details>

<details><summary>On what Operating Systems can I run the OpenBB Terminal?</summary>
<p>

The OpenBB Terminal is compatible with Windows, Mac Os and Linux. Check the
[installation guide](/terminal/quickstart/installation) and [requirements outline](/terminal/quickstart/requirements) for more details.

</p>
</details>

<details><summary>How much hard drive space is required?</summary>
<p>

An installation will use approximately 2GB of space.

</p>
</details>

<details><summary>How can I contribute to the OpenBB Terminal</summary>
<p>

There are three main ways of contributing to this project.

**BECOME A CONTRIBUTOR**

1. Fork the [Project](https://github.com/OpenBB-finance/OpenBBTerminal)
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Install the pre-commit hooks by running: `pre-commit install`
      Any time you commit a change, linters will be run automatically. On changes, you will have to re-commit
4. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to your Branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

You can read more details about adding a feature in our [CONTRIBUTING GUIDELINES](https://github.com/OpenBB-finance/OpenBBTerminal/blob/main/CONTRIBUTING.md).

**RAISE AN ISSUE OR REQUEST A FEATURE**

- Raise an issue by opening a [bug ticket](https://github.com/OpenBB-finance/OpenBBTerminal/issues).
- Request a new  feature through a [feature request ticket](https://github.com/OpenBB-finance/OpenBBTerminal/issues).

</p>
</details>

## Support

<details><summary>How do I report a bug?</summary>
<p>

First, search the open issues for another report. If one already exists, attach any relevant information and screenshots as a comment. If one does not exist, start one with this [link](https://github.com/OpenBB-finance/OpenBBTerminal/issues/new?assignees=&labels=type%3Abug&template=bug_report.md&title=%5BBug%5D)

</p>
</details>

<details><summary>How can I get help with OpenBB Terminal?</summary>
<p>

You can get help with OpenBB SDK by joining our [Discord server](https://openbb.co/discord) or contact us in our support form [here](https://openbb.co/support).

</p>
</details>

## Functionality

<details><summary>Why is data from today missing when I use the load function?</summary>
<p>

By default, the load function requests end-of-day daily data and is not included until the EOD summary has been published. The current day's data is considered intraday and is loaded when the `interval` argument is present.

</p>
</details>

<details><summary>Why does a specific menu or command not exist?</summary>
<p>

It could be that you are running an outdated version in which the menu or command is not yet available. Please check use the [installation guide](https://docs.openbb.co/terminal/quickstart/installation) to download the most recent release.

Do note that it is also possible that the menu or command is removed. If this is undesirable, please reach out to us [here](https://openbb.co/support).

</p>
</details>

## Source

<details><summary>How do I update the OpenBB Terminal?</summary>
<p>

The terminal is constantly being updated with new features and bug fixes, hence, for your terminal to be update, you can use `git pull` to get the latest changes:

```bash
git pull
```

If this fails due to the fact that you had modified some python files, and there's a conflict with the updates, you can use:

```bash
git stash
```

Then, re-run `poetry install` to get any new dependencies. Once installation is finished, you're ready to use the OpenBB Terminal again. If you `stashed` your changes previously, you can un-stash them with:

```bash
git stash pop
```

**NOTE:** When you close the terminal and re-open it, the only command you need to re-call is `conda activate obb`
before you call `openbb` again.

</p>
</details>

<details><summary>Why do I get too many red error lines on Windows?</summary>
<p>


If you are on Windows and your terminal has too many red error lines, it is likely that this is the issue. Go to this page and install the 2019 Build Tools (not the latest) found [here](https://answers.microsoft.com/en-us/windows/forum/windows_other-windows_install/microsoft-visual-c-140/6f0726e2-6c32-4719-9fe5-aa68b5ad8e6d)

</p>
</details>

<details><summary>What does it mean if it says wheel is missing?</summary>
<p>

If you receive any notifications regarding `wheel` missing, this could be due to this dependency missing.

`conda install -c conda-forge wheel` or `pip install wheel`

</p>
</details>

<details><summary>Why do these .whl files not exist?</summary>
<p>

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

1. `poetry update --lock`

2. `conda deactivate` -> `conda activate obb`, then try again

3. Track down the offensive package and purge it from your anaconda `<environment_name>` folder, then try again
   (removing through conda can sometimes leave locks behind)

   | Platform  | Location                                     |
   | --------- | -------------------------------------------- |
   | Linux/Mac | "~/anaconda3/envs" or "~/opt/anaconda3/envs" |
   | Windows   | "%userprofile%/anaconda3/envs"               |

4. Completely nuke your conda environment folder and make a new environment from scratch

5. Reboot your computer and try again

6. Submit a ticket on GitHub

</p>
</details>

<details><summary>What does the JSONDecodeError mean during poetry install?</summary>
<p>

Sometimes poetry can throw a `JSONDecodeError` on random packages while running `poetry install`. This can be observed on macOS 10.14+ running python 3.8+. This is because of the use of an experimental installer that can be switched off to avoid the mentioned error. Run the code below as advised [here](https://github.com/python-poetry/poetry/issues/4210) and it should fix the installation process.

```bash
poetry config experimental.new-installer false
```

</p>
</details>

<details><summary>Why do a receive a ModuleNotFoundError?</summary>
<p>

In the case when you run into an error of the form `ModuleNotFoundError: No module named '_______'` before you start installing these modules that have not been found please check that you have most followed the recommended installation instructions.
These errors often can occur when you have not activated the virtual environment where you have installed the terminal, or you have not used the `poetry install` command to install the dependencies.

In case you wish to proceed with an alternative way to install the terminal feel free to install the missing packages via pip. For example if you get the error that `yfinance` is not found, you would run `pip install yfinance`

</p>
</details>

<details><summary>How do I fix "Cannot convert a symbolic Tensor..."?</summary>
<p>

If you run into issues installing or `Cannot convert a symbolic Tensor...` at runtime, try this:

```bash
poetry install
poetry install -E prediction
```

_Commands that may help you in case of an error:_

- `python -m pip install --upgrade pip`
- `poetry update --lock`
- `poetry install`

</p>
</details>

<details><summary>How do I deal with errors regarding CRLF?</summary>
<p>

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

</p>
</details>

<details><summary>Why can't I run openbb via the VS Code integrated terminal?</summary>
<p>

This occurs when VS Code terminal python version/path is different from the terminal version.

To fix it add this to vscode JSON settings ([ref](https://stackoverflow.com/questions/54582361/vscode-terminal-shows-incorrect-python-version-and-path-launching-terminal-from)):

```bash
    "terminal.integrated.inheritEnv": false,
```

</p>
</details>
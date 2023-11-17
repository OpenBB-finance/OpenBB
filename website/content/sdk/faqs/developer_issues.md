---
title: Developer Issues
sidebar_position: 7
description: A comprehensive troubleshooting guide for developers regarding common
  issues such as launching in debug mode, dealing with GitHub pull requests, git pull
  errors, missing 'wheel', non-existent .whl files, handling JSONDecodeError, correcting
  CRLF errors, running OpenBB via VS Code integrated terminal, and more.
keywords:
- Developer Issues
- Debug mode
- GitHub pull requests
- git pull error
- wheel missing
- whl files
- JSONDecodeError
- CRLF error
- VS Code integrated terminal
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Developer Issues - Faqs | OpenBB SDK Docs" />

<details><summary>How do I launch in debug mode?</summary>

The PyWry window can be run in debug mode for identifying specific issues.  Use the code block below - with the `obb` Python environment active - to import the OpenBB SDK in debug mode.

```python
import os
from openbb_terminal.core.plots.backend import plots_backend

os.environ["DEBUG_MODE"] = "True"
plots_backend().start(True)

from openbb_terminal.sdk import openbb
```

The charts and tables will now include a developer tools button, located at the top-left of the window.

</details>

<details><summary>What branch on GitHub should pull requests be submitted to?</summary>

Pull requests submitted to the Main branch will not be merged, please create branches from the `develop` branch.

To switch to the develop branch:

```console
git checkout develop
```

Branches must also follow the naming convention:

- /feature/name_your_branch
  - For developing functionality.
- /hotfix/name_your_patch
  - For bug patches.

</details>

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

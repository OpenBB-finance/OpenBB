---
title: Installation and Updates
sidebar_position: 1
description: Installation and Updates to the OpenBB SDK.
keywords:
  [
    installation,
    installer,
    install,
    guide,
    mac,
    windows,
    linux,
    python,
    github,
    macos,
    how to,
    explanation,
    openbb sdk,
    pypi,
    miniconda,
    library,
    C++,
    library,
    error
  ]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Installation and Updates - SDK | OpenBB Docs" />

## Installation and Updates

<details><summary>"Microsoft Visual C++ 14.0 or greater is required"</summary>

Download and install [C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/), restart the machine, then try again.

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/ceb57be0-6dae-42f2-aca6-bf62ce7d6135)

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/f8aef8fc-a080-4164-bd36-460714ec44f3)

</details>

<details><summary>Do I have to use Miniconda?</summary>

There are certain dependencies which are sourced exclusively from the `conda-forge` directory. Other virtual environment managers, such a `venv`, may not solve the environment properly, resulting in failed package installations or incorrect builds. We highly recommend using Miniconda as the Python virtual environment manager for installing the OpenBB SDK.

</details>

<details><summary>How do I update my installation to the latest version?</summary>

The code is constantly being updated with new features and bug fixes. The process for updating will vary by the installation type:

- For a `pip` installation, when a new version is published: `pip install -U openbb[all]`
- Upgrade a cloned version of the GitHub repo with:

```console
git fetch
git pull
poetry install -E all
```

**Notes:** If the cloned repository is a fork, pull from: `git pull origin main`, or, `git pull origin develop`. If there are changes locally to the files that conflict with the incoming changes from GitHub, stash them before pulling from main with `git stash`.

</details>

### PyPi Nightly

The nightly build can be installed with:

```console
pip install openbb-nightly[all]
```

**Note**: This version may not be stable and should not be used in a production setting.

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

Additionally, Mac users should install Rosetta:

```console
softwareupdate --install-rosetta
```

</details>

<details><summary>Miniconda3 will not install on ARM/Linux Raspberry Pi machines.</summary>

Refer to this issue on the Conda [GitHub](https://github.com/conda/conda/issues/10723) page.

</details>

<details><summary>Error: Library not loaded: '/usr/local/opt/libomp/lib/libomp.dylib'</summary>

This error is resolved by installing libomp from Homebrew:

```console
brew install libomp
```

</details>

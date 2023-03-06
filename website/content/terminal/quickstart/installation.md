---
title: Installation
sidebar_position: 2
description: The OpenBB Terminal can be directly installed on a Mac or Windows machine via the installer packages below. While not available for Linux is currently available, it can be installed from the command line in a virtual Python environment.
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
    openbb terminal,
  ]
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import InstallerButton from "@site/src/components/General/InstallerButton";

The OpenBB Terminal can be directly installed on a Mac or Windows machine via the installer packages below. While not available for Linux is currently available, it can be installed from the command line in a virtual Python environment. Having trouble? Reach us on [Discord](https://openbb.co/discord) or visit our [contact page](https://openbb.co/contact).

Follow along with the instructions for the preferred installation method:

:::info Installation Instructions

<Tabs>
  <TabItem value="windows" label="Windows">
  This section provides you with the installation file as well as the guide to install the OpenBB Terminal via Windows (10 or greater).

  **Step 1:** Download the file by clicking on the button.

  <InstallerButton type="windows" href="https://github.com/OpenBB-finance/OpenBBTerminal/releases/download/v2.5.1/Windows.OpenBB.Terminal.v2.5.1.exe" label="Windows Installer" />

  **Step 2:** Open the downloaded file by double-clicking on it

  **Step 3:** Follow the prompts to complete the installation process


  **Step 4:** Launch the Terminal by double-clicking on the application shortcut added to the desktop.

  **Note:** The first launch may take up to a few minutes, subsequent launches will be quicker.
</TabItem>
  <TabItem value="mac" label="MacOS">

  Install the OpenBB Terminal on MacOS (Big Sur or later). There are two versions of the installers available for MacOS, Intel-based and Apple Silicon (M1) . <b>Apple Silicon users will need to install Rosetta prior to installation</b>. 

  To understand whether you are using an Apple Sillicon (M1) device or an Intel-based device click on the Apple Icon at the top left of your MacBook and select "About This Mac". Then under "Chip" if it says something like "Apple M1 Pro" or "Apple M1 Max", you know you have an Apple Silicon MacBook. If it says for example "2,3 GHz Quad-Core Intel Core i7" you know that you have an Intel-based MacBook and you can continue by clicking on the "Mac Intel Installer" button.

  <details><summary>Rosetta Installation Instructions (Apple Sillicon users only)</summary>

  1. Press ⌘ (Command) + SPACE to open spotlight search, and type `Terminal` and hit Return (⏎).
  2. Copy and paste the following code in the Terminal and hit ENTER (⏎):
    ```console
    softwareupdate --install-rosetta
    ```
  3. This will start up the Rosetta installation process and you will receive a message regarding the Licence Agreement. Type `A` and hit Return (⏎).
  4. After the installation process has finished, you can proceed t the "Mac M1 Installer" button.


  </details>

  Once all of this is confirmed, you can use the following installation buttons.

  <p>
  <InstallerButton href="https://github.com/OpenBB-finance/OpenBBTerminal/releases/download/v2.5.1/x86.64.MacOS.OpenBB.Terminal.v2.5.1.dmg" label="Mac Intel Installer" />  <InstallerButton href="https://github.com/OpenBB-finance/OpenBBTerminal/releases/download/v2.5.1/ARM64.MacOS.OpenBB.Terminal.v2.5.1.dmg" label="Mac M1 Installer" />
  </p>
  
  Step by step instructions:

  **Step 1:** Download the DMG file from the links above.

  **Step 2:** Mount the downloaded DMG file by double-clicking on it.

  **Step 3:** Click and drag the OpenBB Terminal folder and hold it over the Applications shortcut. This opens a new Finder window, then drag the OpenBB Terminal folder into the Applications folder.

  ![MacOS Installation](https://user-images.githubusercontent.com/11668535/173027899-9b25ae4f-1eef-462c-9dc9-86086e9cf197.png)

  **Step 4:** Unmount the installer, by "Ejecting OpenBB Terminal" from, locations, in Finder.

  **Step 5:** Launch the application by double-clicking on the `OpenBB Terminal` application.

  **Note:** During the first launch, a warning message may appear. Click, "Open".

  ![MacOS Installation](https://user-images.githubusercontent.com/85772166/220201620-1c42bbd4-7509-41fc-8df8-389f34fde58a.png)
  
</TabItem>
  <TabItem value="docker" label="Docker">
    
  Installing the OpenBB Terminal via Docker supports both Windows and Unix systems (Linux + MacOS). Installation differs a bit between operating system (Windows, macOS and Linux). Please select the section matching to your OS.<p></p>

  
  <details><summary>Windows</summary>

  **Install Docker Desktop**

  You can find `Docker Desktop` for MacOS here: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)

  **Start Docker**

  Execute the following command:

  ```console
  docker info
  ```

  If you have something like this, it means you haven't started Docker:

  ```console
  docker info
  Server:
  ERROR: Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
  Is the docker daemon running?
  ```

  Start Docker, this is how the right output looks like:

  ```console
  docker info
  Client:
  Context:    default
  Debug Mode: false

  Server:
  Containers: 14
    Running: 2
    Paused: 1
    Stopped: 10
  ```

  **Install VcXsrv**

  To display charts with your container, you need: VcXsrv.

  You can download VcXsrv here: [Download VcXsrv](https://sourceforge.net/projects/vcxsrv)

  When running VcXsrv program check the option: `Disable access control`

  **Pull and run the container**

  Execute this commands:

  ```console
  curl -o docker-compose.yaml https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/build/docker/docker-compose.yaml

  docker compose run openbb
  ```

  This will download and run the file: `docker-compose.yaml`

  This file contents the settings to pull and run OpenBB Terminal Docker image.
  </details>

  <details><summary>MacOS</summary>

  **Install Docker Desktop**

  You can find `Docker Desktop` for Linux here: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)

  **Start Docker**

  Execute the following command:

  ```console
  docker info
  ```

  If you have something like this, it means you haven't started Docker:

  ```console
  docker info
  Server:
  ERROR: Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
  Is the docker daemon running?
  ```

  Start Docker, this is how the right output looks like:

  ```console
  docker info
  Client:
  Context:    default
  Debug Mode: false

  Server:
  Containers: 14
    Running: 2
    Paused: 1
    Stopped: 10
  ```

  **Install XQuartz**

  You can download XQuartz here: [Download XQuartz](https://www.xquartz.org)

  Open X Quartz.

  Then on `Preferences > Security`.

  Make sure both of these options are enabled:

  - `Authenticate connections`
  - `Allow connections from network clients`

  It should look like this:
  ![Screen Shot 2021-09-08 at 12 21 48 PM](https://user-images.githubusercontent.com/18151143/132548605-235d774b-9aa6-4a45-afcf-58fb775d376a.png)

  **Get Docker IP**

  To get Docker IP you can use this command:

  ```bash
  IP=$(ifconfig | grep inet | grep -v "127.0.0.1" | awk '$1=="inet" {print $2}')
  ```

  **Pull and run the container**

  Execute this commands:

  ```console
  curl -o docker-compose.yaml https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/build/docker/docker-compose.yaml

  xhost +$IP
  docker compose run -e DISPLAY=$IP:0 openbb
  ```

  This will download and run the file: `docker-compose.yaml`

  This file contents the settings to pull and run OpenBB Terminal Docker image.

  The `xhost +$IP` and `DISPLAY=$IP:0` parts are there to allow charts display.


  </details>

  <details><summary>Linux</summary>

  **Install Docker Desktop**

  You can find `Docker Desktop` for Windows here: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)

  **Start Docker**

  Execute the following command:

  ```console
  docker info
  ```

  If you have something like this, it means you haven't started Docker:

  ```console
  docker info
  Server:
  ERROR: Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
  Is the docker daemon running?
  ```

  Start Docker, this is how the right output looks like:

  ```console
  docker info
  Client:
  Context:    default
  Debug Mode: false

  Server:
  Containers: 14
    Running: 2
    Paused: 1
    Stopped: 10
  ```

  **Pull and run the container**

  Execute this commands:

  ```console
  curl -o docker-compose.yaml https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/build/docker/docker-compose.yaml

  xhost +local:
  docker compose run openbb
  ```

  Note: if you're using remote docker host, you can connect with `ssh -X <FQDN/IP>`.

  </details>

  ---

</TabItem>
  <TabItem value="source" label="Source">

  This section guides you a long to install the OpenBB Terminal via Python. This installation type supports both Windows and Unix systems (Linux + MacOS).

  Before starting the installation process, make sure you the following pieces of software are installed.

  <details><summary>Miniconda</summary>
  Miniconda is a Python environment and package manager. It is required for installing certain dependencies.

  Go [here](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links) to find the download for your operating system or use the links below:

  - Apple-Silicon Systems: [Miniconda for MacOS](https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.pkg)
  - Intel-based Mac Systems: [Miniconda for MacOS](https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh)
  - Linux and WSL Systems: [Miniconda for Linux](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh)
  - Raspberry PI Systems: [Miniconda for Raspberry PI](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh)
  - Windows Systems: [Miniconda for Windows](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe)


  **NOTE for Apple Silicon Users:** Install Rosetta from the command line: `softwareupdate --install-rosetta`

  **NOTE for Windows users:** Install/update Microsoft C++ Build Tools from [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
  </details>

  <details><summary>CMake (Mac and Linux only)</summary>
  If you have a **MacBook**, check if homebrew is installed by running `brew --version`

  If Homebrew is not installed, run:

  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  brew install cmake
  brew install gcc
  ```

  If Homebrew is already installed:

  ```bash
  brew install cmake
  brew install gcc
  ```

  If you have a **Linux** computer, use the following script:

  ```bash
  sudo apt update && sudo apt upgrade
  sudo apt install -y gcc cmake
  ```
  </details>

  <details><summary>VcXsrv (Windows and Linux only)</summary>
  Since a WSL installation is headless by default (i.e., there is only access to a terminal running a Linux distribution) there are additional steps required to display visualizations. A more detailed tutorial is found, [here](https://medium.com/@shaoyenyu/make-matplotlib-works-correctly-with-x-server-in-wsl2-9d9928b4e36a).

  - Dynamically export the DISPLAY environment variable in WSL2:

  ```console
  # add to the end of ~/.bashrc file
  export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
  # source the file
  source ~/.bashrc
  ```

  - Download and install [VcXsrv](https://sourceforge.net/projects/vcxsrv/)
  - When running the program is important to check "Disable access control"

  After this, `VcXsrv` should be running successfully, and the machine is ready to proceed with the terminal installation.

  Alternatives to `VcXsrv` include:

  - [GWSL](https://opticos.github.io/gwsl/)
  - [Xming](https://xming.en.softonic.com/)
  - [Wayland](https://wayland.freedesktop.org/docs/html/)


  </details>

  Once you have met all of these requirements, you are ready to install the OpenBB Terminal.


  **Creating a virtual environment**

  When a terminal window is opened, if the base Conda environment - look for `(base)` to the left of the cursor on the command line - is not activated automatically, find the path for it by entering:

  ```console
  conda env list
  ```

  Copy the path which corresponds with `base`, and activate it with:

  ```console
  conda activate REPLACE_WITH_PATH
  ```

  Check which `conda` version is installed by entering:

  ```console
  conda -V
  ```

  Create the environment by copying the code below into the command line:

  ```console
  conda create -n obb -c conda-forge python=3.10.9 pip pybind11 cmake git cvxpy lightgbm poetry
  ```

  **Activate the obb environment**

  After the packages from the previous step are installled, activate the newly created environment by entering:

  ```console
  conda activate obb
  ```

  **Install OpenBB Terminal**

  From your code editor or command line, browse to the location the OpenBB Terminal source code should live. Make sure you have completed the previous steps.

  This starts by cloning the GitHub repository. This will download the source code to the current working directory.

  ```console
  git clone https://github.com/OpenBB-finance/OpenBBTerminal.git
  ```

  Then, navigate to this folder. This can be done in command line or through the code editor by opening the folder.

  ```console
  cd OpenBBTerminal
  ```

  There are a few packages that required to be installed. This is done through Poetry, a package manager.

  ```bash
  pip install qdldl==0.1.5.post3
  poetry install -E all
  ```

  Once this installation process is completed, you can start the terminal by running:

  ```bash
  python terminal.py
  ```

  **NOTE:** When you are opening the OpenBB Terminal from a Terminal application, the Python environment will need to be activated again - `conda activate obb` - and the current working directory should be the `OpenBBTerminal` folder where the source code was cloned. When using a code editor, make sure that you have the correct environment selected. This should be easy to figure out if you get an error that you are missing packages.

  **TROUBLESHOOTING:** Having difficulty getting through the installation, or encountering errors? Check out the [troubleshooting page](/terminal/quickstart/troubleshooting), or reach out to our [Discord](https://discord.gg/Up2QGbMKHY) community for help.

  **Advanced: About Poetry**

  By default we advise using `conda` and `poetry` for environment setup and dependency management. Conda ships binaries for packages like `numpy` so these dependencies are not built from source locally by `pip`. Poetry solves the dependency tree in a way that the dependencies of dependencies of dependencies use versions that are compatible with each other.

  For `Conda` environments, the `build/conda` folder contains multiple `.yaml` configuration files to choose from.

  When using other python distributions we highly recommend a virtual environment like `virtualenv` or `pyenv` for installing the terminal dependency libraries.

  Requirements files that are found in the project root:

  - `requirements.txt` list all the dependencies without Machine Learning libraries
  - `requirements-full.txt` list all the dependencies with Machine Learning libraries

  They can be installed with `pip`:

  ```bash
  pip install -r requirements.txt
  ```

  The dependency tree is solved by poetry.

  Note: The libraries specified in the requirements files have been tested and work for the purpose of this project, however, these may be older versions. Hence, it is recommended for the user to set up a virtual python environment prior to installing these. This allows to keep dependencies required by different projects in separate places.

</TabItem>

</Tabs>
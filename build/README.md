# Building Installers
This guide serves to assist developers construct OpenBB Terminal installers on MacOs and Windows.

## Overview
Building an installer  takes source code as input and produces deployable software as an output. For MacOS the output is a DMG while for windows it is an EXE. This process utilizes two major modules: Pyinstaller & Create-dmg. Windows additionally recruits the service of NSIS. There are two ways to build an installer: locally or through Github.

## Local
In this section we detail the steps necessary to construct an installer locally on a windows machine and mac machine. These steps can be performed on either one of these operating systems so long as they have the OpenBBTerminal repository codebase. This process assumes you already have a working conda environment. Building locally usually takes anywhere from 10-20 minutes.

### MacOS Steps
1. `brew install create-dmg`

    This installs create-dmg and it’s dependencies onto your system through brew.

1. `poetry install -E installer`

    This install pyinstaller and it’s dependencies onto your environment.

3. `build/pyinstaller/build4mac.sh`

    This runs a shell script that auto-builds the DMG and stores it on the root of your repository.

4. (Optional) `/Full/Path/To/OpenBB\ Terminal/.OpenBB/OpenBBTerminal /Full/Path/To/OpenBBTerminal/OpenBBTerminal/scripts/*.openbb -t`

    This runs integration tests on your newly created installer.

### Windows Steps
1. `poetry install -E installer`

    This install pyinstaller and it’s dependencies onto your environment.

2. `pyinstaller build/pyinstaller/terminal.spec`

    This runs a shell script that auto-builds the DMG and stores it on the root of your repository.

3. `cp -r .\dist\OpenBBTerminal\ .\build\nsis\app\`

    This copies over the contents of the newly dist folder into the app folder so that NSIS can utilize them.

4. Compile NSIS Scripts

    Open *NSIS*, click on the "Compile NSI scripts", and then drag the `setup.nsi` file in build\nsis to the window. This creates the EXE installer.

4. (Optional) `Full\Path\To\OpenBBTerminal.exe Full\Path\To\OpenBBTerminal\OpenBBTerminal\scripts -t`

    This runs integration tests on your newly created installer.


## Github
In order to utilize the automated build workflow on the OpenBBTerminal repo, the branch in which you would like to build an installer from must already be a branch on the repo. You can also utilize the automated build workflow on a PR that is from a branch on the repo. You cannot run an automated build on a forked branch or even a PR from a forked branch.

If you are using this method to create an installer, there is a limitation where only one build automation can occur at a time per workflow. For example if there is already an installer being created on the the ‘Intel MacOS Build’ workflow, any subsequent requests for building will be queued. Additionally, the ‘Windows10 Build’ workflow runs relatively slowly because of the size of the EC2 instance it is currently on. As such, if you are interested in a quick build, then I would suggest building locally. Furthermore, building an installer this way also automatically runs integration tests on the installer.

If you run into a circumstance where a requested build is queued for a long period of time, this might mean that the EC2 instance is not connected to github. If something like this arises, please create an issue.

### Steps
1. Navigate to `Actions`
2. Navigate to your desired build system workflow
3. Choose your desired branch & click Run Workflow
4. Download your installer artifact

   Each build system produces a single installer which can be subsequently downloaded.

5. Investigate the success/failure of your Build

    You can click on the build to delve into the steps it takes to construct an installer. This is where you can investigate the success of integration tests, identify if/where the build failed, etc.


Note: Intel Mac installers are signed and notarized. During this step you can identify if notarization has succeeded or failed and if all of the binaries have been signed in correctly.

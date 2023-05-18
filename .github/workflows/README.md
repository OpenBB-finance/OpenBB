# OpenBB Terminal Github Actions Workflow
## This document aims to describe/define the functional requirements for GitHub Action workflows in OpenBBTerminal Repo.

*   [1\. OpenBB Terminal Github Processes](#GitHubActionsFunctionalRequirements-1.OpenBBTerminalGithubProcesses)
    *   [1.1. Release Process](#GitHubActionsFunctionalRequirements-1.1.ReleaseProcess)
    *   [1.2. Nightly Build](#GitHubActionsFunctionalRequirements-1.2.NightlyBuild)
    *   [1.3. Adding a feature](#GitHubActionsFunctionalRequirements-1.3.Addingafeature)
    *   [1.4. Adding a hotfix](#GitHubActionsFunctionalRequirements-1.4.Addingahotfix)
    *   [1.5. Manual Installer Build (Developer Testing)](#GitHubActionsFunctionalRequirements-1.5.ManualInstallerBuild(DeveloperTesting))
*   [2\. List of the workflows](https://github.com/OpenBB-finance/OpenBBTerminal/tree/feature/improve-workflow-readme/.github/workflows#2-list-of-the-workflows)
    *   [2.1. Branch Name Check](https://github.com/OpenBB-finance/OpenBBTerminal/tree/feature/improve-workflow-readme/.github/workflows#21-branch-name-check-done)
    *   [2.2. Build & Release](#GitHubActionsFunctionalRequirements-2.2.Build&ReleasGreen)
    *   [2.3. Build and Publish Docker](#GitHubActionsFunctionalRequirements-2.3.BuildandPublishDockeGreen)
    *   [2.4. Release Drafter](#GitHubActionsFunctionalRequirements-2.4.ReleaseDrafteGreen)
    *   [2.5. Deploy to GitHub Pages](#GitHubActionsFunctionalRequirements-2.5.DeploytoGitHubPageGreen)
    *   [2.6. Integration Tests](#GitHubActionsFunctionalRequirements-2.6.IntegrationTests)
    *   [2.7. General Linting](#GitHubActionsFunctionalRequirements-2.7.GeneralLintinGreen)
    *   [2.8. MacOS M1 and Intel Build](#GitHubActionsFunctionalRequirements-2.8.MacOSM1andIntelBuilGreen)
    *   [2.9. Mac OS X Full Clean Build with ML](#GitHubActionsFunctionalRequirements-2.9.MacOSXFullCleanBuildwithML)
    *   [2.10. Nightly Build on develop branch](#GitHubActionsFunctionalRequirements-2.10.NightlyBuildondevelopbrancGreen)
    *   [2.11. Deploy to PyPI - Nightly](#GitHubActionsFunctionalRequirements-2.11.DeploytoPyPI-NightlGreen)
    *   [2.12. Deploy to PyPI](#GitHubActionsFunctionalRequirements-2.12.DeploytoPyPGreen)
    *   [2.13. Unit Test](#GitHubActionsFunctionalRequirements-2.13.UnitTesGreen)
    *   [2.14. Windows 10 Full Clean Build with ML](#GitHubActionsFunctionalRequirements-2.14.Windows10FullCleanBuildwithMGreen)
    *   [2.15. Windows10 Build](#GitHubActionsFunctionalRequirements-2.15.Windows10BuilGreen)
    *   [2.16. Reviewpad](#GitHubActionsFunctionalRequirements-2.16.Reviewpad)

1\. OpenBB Terminal Github Processes
------------------------------------

### 1.1. Release Process

**Purpose**  
This process is a guide on how to build a new version of the OpenBB Installer.

**Steps**

*   The user will Create a branch for release from `develop` branch which follows the GitFlow naming convention i.e. `release/x.y.z`
    
*   The user will increment the version number in 3 files: `pyproject.toml` `setup.nsis` `feature_flags.py` and commit the changes
    
*   The [Build & Release](https://openbb.atlassian.net/wiki/spaces/ENG/pages/239829001/GitHub+Actions+Functional+Requirements#2.2.-Build-%26-Release) workflow will be triggered on `push`. This will trigger the workflows to build the installers, publish the docker image and deploy to Pypi.
    
*   The User merges the `release` branch to the `main` and `develop` branch once the release process is completed successfully.
    

**Related Workflows**

*   [Build and Publish Docker](https://openbb.atlassian.net/wiki/spaces/ENG/pages/239829001/GitHub+Actions+Functional+Requirements#2.3.-Build-and-Publish-Docker)
    
*   Release Drafter
    
*   Deploy to GitHub Pages
    
*   Integration Tests
    
*   General Linting
    
*   Unit Test
    

### 1.2. Nightly Build

**Purpose**  
This process is a guide on how to build a beta version of the OpenBB Installer daily. The nightly build is made from the default development branch `develop` and would provide a usable version of the terminal for macOS, windows, docker, and Pypi.

**Steps**

*   This is a workflow that doesn’t require any manual input.
    
*   The User can download terminal installers from the workflow page to get access to daily builds of the current development process
    

**How to use nightly build**

*   SDK - `pip install openbb-nightly`
    
*   Windows Installer:
    
    *   Go to the Nightly Build GitHub Actions Page - [https://github.com/OpenBB-finance/OpenBBTerminal/actions/workflows/nightly-build.yml](https://github.com/OpenBB-finance/OpenBBTerminal/actions/workflows/nightly-build.yml)
        
        ![](/images/nightly.png)
    *   Select the latest nightly build action and click on the `trigger-windows-build` job
        
        ![](/images/nightly-windows.png)
    *   Click on the workflow link
        
        ![](/images/nightly-windows1.png)
    *   Download the installer
        
        ![](/images/nightly-windows2.png)
        
*   MacOs Installer:
    
    *   Go to the Nightly Build GitHub Actions Page - [https://github.com/OpenBB-finance/OpenBBTerminal/actions/workflows/nightly-build.yml](https://github.com/OpenBB-finance/OpenBBTerminal/actions/workflows/nightly-build.yml)
        
        ![](/images/nightly.png)
    *   Select the latest nightly build action and click on the `trigger-macos-build` job
        
        ![](/images/nightly-macos.png)
    *   Click on the workflow link
        
        ![](/images/nightly-macos1.png)
    *   Download the installer
        
        ![](/images/nightly-macos2.png)
        

**Related Workflows**

*   [Nightly Build](https://openbb.atlassian.net/wiki/spaces/ENG/pages/239829001/GitHub+Actions+Functional+Requirements#2.10.-Nightly-Build-on-develop-branch)
    

### 1.3. Adding a feature

*   The user will create a branch from `develop` branch with the name format `feature/new-feature`
    
*   The user can commit changes to their feature branch to trigger the linting test workflow on their branch
    
*   The user will create a pull request to add their feature to the terminal. This will trigger the unit test workflow. When a PR is created, the following CI is triggered  
    \- branch name check  
    \- Linting (markdown & Code linting)  
    \- Unit Test (based on PR state - Merged/Open)
    
    ![](/images/pr.png)
    
    The PR must pass all these checks before it can be merged. The CI will be triggered automatically once the PR process starts (create → merged)
    

**Related Workflows**

*   Branch Name Check
    
*   Unit Test
    
*   General Linting
    

### 1.4. Adding a hotfix

*   The user will create a branch from develop branch with the name format `hotfix/new-hotfix`
    
*   The user can commit changes to their hotfix branch to trigger the linting test workflow on their branch
    
*   The user will create a pull request to add their hotfix to the main branch. When a PR is created from the hotfix branch to the main branch, the following CI is triggered  
    \- branch name check  
    \- Linting (markdown & Code linting)  
    \- Unit Test (based on PR state - Merged/Open)
    
    ![](/images/pr.png)
    
    The PR must pass all these checks before it can be merged. The CI is triggered automatically once the PR process starts (create → merged).
    
*   The user will merge the successful hotfix branch to the main will trigger the build & release workflow to build the install and deploy docker image and publish it to PyPI.
    

**Related Workflows**

*   Branch Name Check
    
*   Unit Test
    
*   General Linting
    

### 1.5. Manual Installer Build (Developer Testing)

**Purpose**  
Developers/Contributors can use this process to quickly test a feature they are working on with a standalone installer. The build can be triggered on any branch as shown below

![](/images/installer-build1.png)

**Steps**

*   The user will select the workflow based on the operating system that will be tested  
    \- [Windows CI](https://github.com/OpenBB-finance/OpenBBTerminal/actions/workflows/windows10_build.yml)  
    \- [MacOS CI](https://github.com/OpenBB-finance/OpenBBTerminal/actions/workflows/macos-build.yml)
    
*   The user will select the branch that will be used to build the installer and run the workflow
    
    ![](/images/installer-build.png)
*   A standalone installer will be generated on completion of the workflow which can then be installed on the user machine
    
    ![](/images/nightly-macos2.png)

2\. List of the workflows
-------------------------

### 2.1. Branch Name Check

**Workflow Url:** [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/branch-name-check.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/branch-name-check.yml)

**Description**: This workflow checks the branch names of pull requests to ensure they follow the GitFlow naming convention. Pull requests to the 'develop' branch must come from the 'main', 'feature/\*', 'hotfix/\*', or 'release/\*' branches. Pull requests to the 'main' branch must come from the 'hotfix/\*' or 'release/\*' branches.

**Triggers**: The workflow will be triggered on pull requests for the 'develop' and 'main' branches. The trigger event types include: opened, synchronize, and edited.

**Artifacts**: None

**Conditions**: The workflow will only run if the following conditions are met:

*   The pull request targets the 'develop' or 'main' branch.
    
*   The source branch follows the GitFlow naming convention.
    

**Inputs**: The workflow does not require any inputs.

**Outputs**:

*   The action will provide clear feedback on the branch name validation process, including success or failure messages.
    
*   The action will display the source and target branch names in the output.
    

### 2.2. Build & Release

**Workflow Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/build-release.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/build-release.yml)

**Description**: This workflow triggers builds for Windows, MacOS (Intel & M1), and Docker environments. It dispatches separate workflows for each build environment and waits for their completion.

**Triggers**: The workflow will be triggered on pushes to the 'release/\*' and 'main' branches.

**Artifacts**: Installers will be provided for the Windows and macOS builds on completion

**Conditions**: The workflow will only run if the following conditions are met:

*   The push event occurs on the 'release/\*' or 'main' branch.
    

**Inputs**: The workflow does not require any inputs.

**Outputs**:

*   The action will trigger Windows, MacOS, and Docker builds by dispatching separate workflows.
    
*   The action will wait for the completion of each build with a timeout of 2 hours.
    

### 2.3. Build and Publish Docker

**Workflow Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/docker-build.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/docker-build.yml)

**Description**: This workflow builds and publishes a Docker image of the application to the GitHub Container Registry. The image is built using the provided Dockerfile and .env configuration. It publishes a release version of the image when the workflow is triggered on the 'main' branch and also publishes the latest version of the image.

**Triggers**: The workflow will be triggered manually using the `workflow_dispatch` event or when triggered by other workflows e.g. Build/Release or Nightly Build Workflows.

**Artifacts**: None

**Conditions**: The workflow will only run if the following conditions are met:

*   The workflow is manually triggered.
    
*   The workflow is called from another workflow.
    

**Inputs**: The workflow does not require any inputs.

**Outputs**:

*   The action will build the Docker image based on the provided Dockerfile and .env configuration.
    
*   The action will publish the Docker image to the GitHub Container Registry:
    
    *   A release version of the image will be published if the workflow is triggered on the 'main' branch.
        
    *   The latest version of the image will also be published if the workflow is triggered on the 'main' branch.
        

### 2.4. Release Drafter

**Workflow Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/draft-release.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/draft-release.yml)

**Description**: This workflow automatically creates or updates a draft release based on the latest changes in the repository using the Release Drafter action. It helps in maintaining a consistent format for release notes and eases the process of creating release notes for new releases.

**Triggers**: The workflow will be triggered manually using the `workflow_dispatch` event.

**Artifacts**: None

**Conditions**: The workflow will only run if the following conditions are met:

*   The workflow is manually triggered.
    

**Inputs**: The workflow does not require any inputs.

**Outputs**:

*   The action will create or update a draft release based on the latest changes in the repository.
    
*   The draft release will follow a pre-defined format as specified in the Release Drafter configuration file.
    

### 2.5. Deploy to GitHub Pages

**Workflow Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/gh-pages.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/gh-pages.yml)

**Description**: This workflow generates and deploys the project documentation to GitHub Pages. It builds the website using Python and Node.js and then deploys the generated static files to the `gh-pages` branch.

**Triggers**: The workflow will be triggered on pushes to the 'main' and 'release/\*' branches.

**Artifacts**: None

**Conditions**: The workflow will only run if the following conditions are met:

*   The push event occurs on the 'main' or 'release/\*' branch.
    

**Inputs**: The workflow does not require any inputs.

**Outputs**:

*   The action will generate the project documentation using Python and Node.js.
    
*   The action will build the website using the provided configuration and assets.
    
*   The action will deploy the generated static files to the `gh-pages` branch on GitHub Pages.
    

### 2.6. Integration Tests

**Workflow-Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/integration-test.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/integration-test.yml)

**Description**: This workflow runs integration tests on the application, and then reports the test results to a specified Slack channel. The test results are posted as a file attachment along with a summary message in the Slack channel.

**Triggers**: The workflow will be triggered on pushes to the 'main' and 'release/\*' branches, and can also be manually triggered using the 'workflow\_dispatch' event.

**Artifacts**: None

**Conditions**: The workflow will only run if the following conditions are met:

*   The push event occurs on the 'main' or 'release/\*' branch, or the 'workflow\_dispatch' event is triggered.
    

**Inputs**: The workflow does not require any inputs.

**Outputs**:

*   The action will run integration tests on the application.
    
*   The action will post a summary message to the specified Slack channel, along with the test results as a file attachment.
    
*   The action will send a notification to the Slack channel when the workflow starts, and another notification with the workflow's success or failure status.
    

### 2.7. General Linting

**Workflow Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/linting.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/linting.yml)

**Description**: This workflow performs general code linting and Markdown linting to maintain code quality and consistency in the project. It checks for code issues, formatting inconsistencies, spelling errors, and broken links in the Markdown files.

**Triggers**: The workflow is triggered on the following events:

*   Pull requests (on opening, synchronizing, and editing).
    
*   Pushes to the `feature/`_,_ `hotfix/`, and `release/*` branches.
    
*   Merge group checks (when requested).
    

**Artifacts**: None

**Conditions**: The workflow will only run if the specified triggers are met.

**Inputs**: The workflow does not require any inputs.

**Outputs**:

*   The action will perform code linting using tools such as Bandit, Black, Codespell, Mypy, Pylint, and Ruff.
    
*   The action will perform Markdown linting using the `avtodev/markdown-lint` Docker image.
    
*   The action will report linting errors and warnings, if any, to help maintain code quality and consistency in the project.
    

### 2.8. MacOS M1 and Intel Build

**Workflow Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/macos-build.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/macos-build.yml)

**Description**: This workflow triggers separate builds for MacOS M1 (ARM64) and Intel (x64) architectures. It dispatches separate jobs for each architecture and waits for their completion. It runs integration tests, signs the package, notarizes it, and uploads the test summary to a Slack channel

**Triggers**: Manual trigger using "workflow\_dispatch" event.

**Artifacts**: Installers will be provided for the M1 and Intel MacOS builds on completion.

**Conditions**: The workflow will only run if the following conditions are met:

*   The workflow will run if manually triggered using the "workflow\_dispatch" event.
    
*   The application is intended for the MacOS platform.
    
*   Triggered by other workflows.
    

**Inputs**: The workflow does not require any inputs.

**Outputs**:

*   The action will trigger separate builds for MacOS M1 and Intel architectures by dispatching separate jobs.
    
*   The action will wait for the completion of each build with a timeout of 2 hours.
    
*   The action will produce installers for the M1 and Intel MacOS builds on completion.
    

### 2.9. Mac OS X Full Clean Build with ML

**Workflow Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/macos-ml.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/macos-ml.yml)

**Description**: This workflow will perform a complete clean build of the project on MacOS with Python 3.9 using Miniconda, and run tests for the application.

**Triggers**: The workflow will be triggered on pushes to the main branch and can also be manually triggered using workflow\_dispatch.

**Artifacts**: No specific artifacts are generated.

**Conditions**: The workflow will only run if the following conditions are met:

*   The branch that was pushed to is the main branch.
    
*   The Checkout, Setup caching for conda packages, Setup Miniconda, Get pip cache dir, pip cache, Uninstall Brotlipy, Install dependencies (Bash), List installed packages (Bash), and Run tests (Bash) jobs succeed.
    

**Inputs**: The workflow requires input for the workflow\_dispatch trigger:

*   comments (required): A description of the test scenario tags.
    

**Outputs**:

*   The action will run tests using pytest on the tests/ directory.
    
*   The action will display information about the conda environment, conda packages, and pip packages.
    
*   The action will start the terminal using [terminal.py](http://terminal.py) and then exit.
    

### 2.10. Nightly Build on develop branch

**Workflow Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/nightly-build.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/nightly-build.yml)

**Description**: This workflow triggers nightly builds for Windows, macOS, Docker, and PyPI environments.

**Triggers**: The workflow is scheduled to run every day at 00:00 UTC on the develop branch.

**Artifacts**:

*   Windows build artifacts
    
*   macOS build artifacts (M1 & Intel)
    

**Conditions**: The workflow will run if the following conditions are met:

*   The scheduled time is reached (00:00 UTC daily).
    

**Inputs**: The workflow does not require any inputs.

**Outputs**:

*   Trigger Windows build using the `windows10_build.yml` workflow.
    
*   Trigger macOS build (both M1 and Intel) using the `macos-build.yml` workflow.
    
*   Trigger Docker build using the `docker-build.yml` workflow.
    
*   Trigger PyPI build using the `pypi-nightly.yml` workflow.
    

### 2.11. Deploy to PyPI - Nightly

**Workflow Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/pypi-nightly.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/pypi-nightly.yml)

**Description**: This workflow builds and publishes nightly distributions of the project to PyPI as an "openbb-nightly" package.

**Triggers**: The workflow is triggered manually using the "workflow\_dispatch" event.

**Artifacts**:

*   Binary wheel distribution
    
*   Source tarball distribution
    

**Conditions**: The workflow will run if the following conditions are met:

*   The workflow is manually triggered using the "workflow\_dispatch" event.
    

**Inputs**: The workflow does not require any inputs.

**Outputs**:

*   Update the package name in the `pyproject.toml` file to "openbb-nightly".
    
*   Update the package version in the `pyproject.toml` file to include the current date as a development version (e.g., "1.0.0.dev20220418").
    
*   Update the installation instructions in the `./website/pypi.md` file to use the "openbb-nightly" package.
    
*   Install the pypa/build package to build the distributions.
    
*   Build a binary wheel and a source tarball distribution.
    
*   Publish the distributions to PyPI using the "openbb-nightly" package name.
    

### 2.12. Deploy to PyPI

**Workflow Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/pypi.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/pypi.yml)

**Description**: This workflow will build and publish the package to TestPyPI and PyPI repositories.

**Triggers**:

1.  The workflow will be triggered on pushes to branches with the pattern `release/*` or `main`.
    
2.  The workflow can also be triggered manually using `workflow_dispatch`.
    

**Artifacts**: None

**Conditions**: The workflow will only run if the following conditions are met:

1.  The build process for the binary wheel and source tarball succeeds.
    

**Inputs**: The workflow does not require any inputs.

**Outputs**:

1.  The action will build a binary wheel and a source tarball for the package.
    
2.  The action will publish the package to TestPyPI if the current branch matches the pattern `release/*`.
    
3.  If the current branch is main, the action will publish the package to PyPI.
    

### 2.13. Unit Test

**Workflow Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/unit-test.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/unit-test.yml)

**Description**: This workflow will run unit tests for the project on various operating systems and Python versions using Poetry and Miniconda for dependency management.

**Triggers**: The workflow will be triggered on pull requests to the `develop` and main branches, on pushes to release/\* branches, and when checks are requested.

**Artifacts**: No specific artifacts are generated, but the workflow uploads coverage reports to Codecov.

**Conditions**: The workflow will only run if the following conditions are met:

*   A pull request is not merged, not a draft, and the event is not a push.
    
*   The base branch for the pull request is 'develop'.
    
*   The check-files-changed, base-test, tests-python, full-test, and tests-conda jobs succeed.
    
*   Runs the full test suite on Ubuntu-latest and macOS-latest with Python 3.8, 3.9, and 3.10 using Poetry when a PR is merged or a push to release/\* branch is made.
    
*   Runs test on Ubuntu, Windows, and macOS using Anaconda Python (Python 3.9) and Conda for dependency management when a PR is merged or a push to release/\* branch is made.
    

**Inputs**: The workflow does not require any inputs.

**Outputs**:

*   The action will run tests using pytest with specified flags and coverage options.
    
*   The action will display information about the installed pip and conda packages.
    
*   The action will start the terminal using [terminal.py](http://terminal.py) and then exit.
    

### 2.14. Windows 10 Full Clean Build with ML

**Workflow Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/windows\_ml.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/windows_ml.yml)

**Description**: This workflow performs a full clean build of the project on a Windows 10 environment with Python 3.9 and runs tests on the build.

**Triggers**:

1.  Pushes to the "main" branch.
    
2.  Manual trigger using "workflow\_dispatch" event with a required "comments" input describing the test scenario tags.
    

**Artifacts**: None.

**Conditions**: The workflow will run if the following conditions are met:

*   The workflow is triggered by a push to the "main" branch or manually using the "workflow\_dispatch" event.
    

**Inputs**:

*   Test scenario tags (required) - Description of the test scenario when manually triggering the workflow using "workflow\_dispatch".
    

**Outputs**:

*   The successful completion of the workflow will indicate that the build and tests have passed, and the environment has been set up correctly.
    

### 2.15. Windows10 Build

**Workflow Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/windows10\_build.yml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/.github/workflows/windows10_build.yml)

**Description**: This workflow will build and deploy the OpenBBTerminal application for Windows 10.

**Triggers**: The workflow will be triggered manually using `workflow_dispatch`.

**Artifacts**:

1.  OpenBB-Windows10-ENV: The OpenBBTerminal application built for Windows 10, compressed as a zip file.
    
2.  Windows EXE Artifact: The OpenBB Terminal Setup.exe file, an NSIS installer for the OpenBBTerminal application.
    

**Conditions**: The workflow will only run if the following conditions are met:

1.  The Windows-Build job succeeds.
    
2.  The Build-Exe job succeeds.
    

**Inputs**: The workflow does not require any inputs.

**Outputs**:

1.  The action will run integration tests on the application.
    
2.  The action will post a summary message to the specified Slack channel, along with the test results as a file attachment.
    
3.  The action will send a notification to the Slack channel when the workflow starts and another notification with the workflow's success or failure status.
    

### **2.16. Reviewpad**

**Name**: Automated PR Review

**Workflow Url**: [https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/reviewpad.yaml](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/reviewpad.yaml)

**Description**: This workflow automates the review process of pull requests by checking for size, sanity, dependency changes, and end-of-file (EOF) line endings. It adds or removes labels based on the size of the PR, verifies that the PR is reviewable, checks for image files, validates dependency changes, and ensures correct line endings.

**Triggers**: The workflow will be triggered on pull requests.

**Artifacts**: None

**Conditions**: The workflow will run on every pull request.

**Inputs**: The workflow does not require any inputs.

**Outputs**:

1.  The action will add or remove labels based on the size of the PR.
    
2.  The action will fail the PR if it is too large or contains image files.
    
3.  The action will request changes or warn if there are issues with dependency files.
    
4.  The action will warn if files have CRLF line endings instead of LF.
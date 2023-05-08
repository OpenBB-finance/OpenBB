# OpenBB Workflows
This directory contains the workflows for the OpenBB 🦋 Project. The workflows are:

| Workflows   | Summary |   Branches
| :-------------------- |:------------------ | :------------------
| branch-name-check.yml | Checks if the branch name is valid and follows the naming convention.                     | all branches
| build-release.yml     | Builds the project and runs the tests.                                                    | main, release/*
| docker-build.yml      | Builds the docker image and pushes it to the docker hub.                                  | all branches (only pushes to docker hub on main)
| draft-release.yml     | Creates a draft release when a new tag is pushed.                                         | -
| gh-pages.yml          | Builds the documentation and deploy to github pages.                                      | main and release/*
| integration-test.yml  | Runs the integration tests.                                                               | all branches
| labels-issue.yml      | Creates an issue when a new bug is reported.                                              | -
| labels-PR.yml         | Adds labels to the issues and pull requests.                                              | -
| linting.yml           | Runs the linters.                                                                         | all branches
| macos-build.yml       | Builds the project on M1 Macs.                                                            | develop, main, release/*
| macos-ml.yml          | Builds the project on Mac OS X Full Clean Build with ML.                                  | main
| nightly-build.yml     | Builds the project and runs the integration tests every night on the `develop` branch.    | develop
| pypi.yml              | Publishes the package to PyPI.                                                            | all branches (only pushes to PyPI on main)
| pypi-nightly.yml      | Publishes the package to PyPI every night on the `develop` branch.                        | develop
| unit-test.yml         | Runs the unit tests.                                                                      | all branches
| windows_ml.yml        | Builds the project on Windows 10 Full Clean Build with ML.                                | main
| windows10_build.yml   | Builds the project on Windows 10.                                                         | all branches

## Branch Name Check Workflow
Objective: To check if pull request branch names follow the GitFlow naming convention before merging.

Triggered by: A pull request event where the target branch is either develop or main.

Branches checked: The source branch of a pull request and the target branch of a pull request.

Steps:

1.  Extract branch names: Using the jq tool, the source and target branch names are extracted from the pull request event. The branch names are then stored in environment variables and printed as output.

2.  Show Output result for source-branch and target-branch: The source and target branch names are printed to the console.

3.  Check branch name for develop PRs: If the target branch is develop, then the source branch is checked against a regular expression to ensure that it follows the GitFlow naming convention. If the branch name is invalid, a message is printed to the console and the workflow exits with a status code of 1.

4.  Check branch name for main PRs: If the target branch is main, then the source branch is checked against a regular expression to ensure that it is either a hotfix or a release branch. If the branch name is invalid, a message is printed to the console and the workflow exits with a status code of 1.

Note: The GitFlow naming convention for branches is as follows:

-   Feature branches: feature/<feature-name>
-   Hotfix branches: hotfix/<hotfix-name>
-   Release branches: release/<major.minor.patch>(rc<number>)

## Build Release Workflow
This GitHub Actions workflow is responsible for building and releasing software for multiple platforms (Windows, M1 MacOS, Intel MacOS, and Docker).
The workflow has four jobs:

-   `trigger-windows-build`
-   `trigger-macos-build`
-   `trigger-intel-build`
-   `trigger-docker-build`

Each job uses the `aurelien-baudet/workflow-dispatch` action to trigger another workflow, respectively `windows10_build.yml`, `m1_macos_build.yml`, `intel_macos_build.yml`, and `docker.yml`. The `GITHUB_TOKEN` is passed as a secret so that the triggered workflows have access to the necessary permissions. The `wait-for-completion-timeout` is set to 2 hours, which is the maximum amount of time the job will wait for the triggered workflow to complete.

## Docker Workflow
This GitHub Actions workflow is responsible for building and pushing the docker image to the itHub Container Registry. This workflow is triggered when a new change is pushed to the main branch of the repository, and the Docker image is published to the GitHub Container Registry.

Steps
-----

1.  Checkout Code: This step checks out the code from the GitHub repository.

2.  Login to GitHub Container Registry: This step logs into the GitHub Container Registry using the GitHub Actions token.

3.  Setup Commit Hash: This step sets the commit hash of the code that is being built.

4.  Build Env File: This step builds the environment file for the Docker image.

5.  Building the Docker Image: This step builds the Docker image using the scripts in the `build/docker` directory.

6.  Publishing the Docker Image: This step publishes the Docker image to the GitHub Container Registry. The Docker image is only pushed to the registry if the branch being built is `main`.

## Release Drafter Workflow
This GitHub Actions workflow is designed to automatically generate and update draft releases in a GitHub repository. The workflow is triggered when it is manually dispatched, allowing you to control when the draft releases are updated.

## GH Pages Workflow
This GitHub Actions workflow is responsible for building the documentation and deploying it to GitHub Pages. This workflow is triggered when a new change is pushed to the `main` or `release` branch of the repository, and the documentation is published to GitHub Pages.

## Integration Test Workflow
This GitHub Action is used to run integration tests on your code repository. It is triggered on pushes to the `release/*` or `main` branches, and it runs on the latest version of Ubuntu.

The workflow consists of the following steps:

1.  Check out the code from the repository
2.  Set up Python 3.9
3.  Install Poetry, a package and dependency manager for Python
4.  Load a cached virtual environment created by Poetry, to speed up the process if possible
5.  Install dependencies specified in the `poetry.lock` file
6.  Run the integration tests using the `terminal.py` script
7.  Upload a summary of the test results to Slack

The results of the tests are captured in a file called `result.txt`. The summary of the tests, including information about failed tests, is then uploaded to Slack using the `adrey/slack-file-upload-action` GitHub Action.

## Linting Workflow
This GitHub Actions workflow is responsible for running linting checks on the codebase. This workflow is triggered on pull request events such as `opened`, `synchronize`, and `edited`, and push events on branches with names that start with `feature/`, `hotfix/`, or `release/`. The workflow also sets a number of environment variables and uses Github Actions caching to improve performance.

It consists of two jobs: `code-linting` and `markdown-link-check`.

The first job, `code-linting`, runs on an Ubuntu machine and performs several linting tasks on the code in the repository, including:

-   Checking out the code from the repository
-   Setting up Python 3.9
-   Installing a number of Python packages necessary for the linting tasks
-   Running `bandit` to check for security vulnerabilities
-   Running `black` to check the code formatting
-   Running `codespell` to check the spelling of comments, strings, and variable names
-   Running `ruff` to check the use of Python
-   Running `mypy` to check the type annotations
-   Running `pyupgrade` to upgrade Python 2 code to Python 3
-   Running `pylint` to perform static analysis of the code

The second job, `markdown-link-check`, runs on an Ubuntu machine and performs linting of the markdown files in the repository. It uses a Docker container `avtodev/markdown-lint` to perform the linting.

## MacOS Build Workflow
This GitHub Actions workflow is used to build a version of the OpenBB Terminal for M1 MacOS. The build process includes installing necessary dependencies, building the terminal application using PyInstaller, creating a DMG file for distribution, and running integration tests on the built application.

Jobs
----

The workflow consists of a single job named `Build` which runs on self-hosted MacOS systems with ARM64 architecture. The job performs the following steps:

1.  Checkout: The main branch of the repository is checked out, allowing for the commit hashes to line up.
2.  Git Log: The log of the Git repository is displayed.
3.  Install create-dmg: The `create-dmg` tool is installed using Homebrew.
4.  Clean Previous Path: The previous PATH environment variable is cleared and restored to its default values.
5.  Setup Conda Caching: The miniconda environment is set up using a caching mechanism for faster workflow execution after the first run.
6.  Setup Miniconda: Miniconda is set up using the `conda-3-9-env-full.yaml` environment file, with channels `conda-forge` and `defaults`, and with the `build_env` environment activated.
7.  Run Poetry: Poetry is used to install the dependencies for the project.
8.  Install PyInstaller: PyInstaller is installed using Poetry.
9.  Poetry Install Portfolio Optimization and Forecasting Toolkits: The portfolio optimization and forecasting toolkits are installed using Poetry.
10. Install Specific Papermill: A specific version of Papermill is installed using pip.
11. Build Bundle: The terminal application is built using PyInstaller, with icons and assets copied to the DMG directory.
12. Create DMG: The DMG file is created using the `create-dmg` tool.
13. Clean up Build Artifacts: The build artifacts such as the terminal directory and DMG directory are removed.
14. Save Build Artifact DMG: The DMG file is saved as a build artifact.
15. Convert & Mount DMG: The DMG file is converted and mounted.
16. Directory Change: The current directory is changed to the mounted DMG file.
17. Unmount DMG: The mounted DMG file is unmounted.
18. Run Integration Tests: The built terminal application is run with integration tests, and the results are displayed.

Finally, the integration tests are run and the results are logged. The workflow is configured to run only when triggered by a workflow dispatch event and runs in a concurrent group, with the ability to cancel in-progress jobs.

## Nightly Build Workflow
This code is a GitHub Actions workflow configuration file that is used to trigger other workflows when certain events occur. The main purpose of this workflow is to trigger builds on different platforms when a release is made or a pull request is made to the main branch.

This workflow is triggered at UTC+0 daily by the GitHub Action schedule event.

The job includes the following steps:

1.  Trigger Windows Build: This step uses the `aurelien-baudet/workflow-dispatch` action to trigger the windows10_build.yml workflow.

2.  Trigger macOS Build: This step uses the `aurelien-baudet/workflow-dispatch` action to trigger the m1_macos_build.yml workflow

3.  Trigger Intel Build: This step uses the `aurelien-baudet/workflow-dispatch` action to trigger the intel_macos_build.yml workflow

4.  Trigger Docker Build: This step uses the `aurelien-baudet/workflow-dispatch` action to trigger the docker.yml workflow

This workflow also uses a concurrency setting that groups the jobs by the workflow and ref, and cancels any in-progress jobs.

## Nightly PyPI Publish Workflow
This workflow is used to publish the latest version of the OpenBB Terminal to PyPI. The workflow is triggered at UTC+0 daily by the GitHub Action schedule event.

It does this by first updating the `pyproject.toml` file with a pre-determined version string of the form `<currentVersion>.dev<date>`, where `<date>` represents the current day's date as a 8 digit number.

Then, the code installs `pypa/build` and uses `python -m build` to create a binary wheel and a source tarball in the `dist/` directory.

Finally, it uses the PyPA specific action `gh-action-pypi-publish` to publish the created files to PyPI. 

## PYPI publish Workflow
The Github Action code `Deploy to PyPI` is used to deploy a Python project to PyPI (Python Package Index) and TestPyPI, which is a separate package index for testing purposes. The code is triggered on two events:

1.  Push event: The code is triggered whenever there is a push to the `release/*` and `main` branches.

2.  Workflow dispatch event: The code can be manually triggered by the workflow dispatch event.

The code sets the concurrency to the `group` and the option `cancel-in-progress` is set to `true` to ensure that the running jobs in the same `group` are cancelled in case another job is triggered.

The code contains two jobs, `deploy-test-pypi` and `deploy-pypi`, both of which have the same steps with slight variations.

The `deploy-test-pypi` job is triggered only if the pushed branch starts with `refs/heads/release/`. This job sets up the Python environment, installs the `build` package using `pip`, builds binary wheel and source tarball using `build`, and finally, publishes the distributions to TestPyPI using the `pypa/gh-action-pypi-publish@release/v1` Github Action. The `password` to access TestPyPI is stored as a secret named `TEST_PYPI_API_TOKEN`.

Similarly, the `deploy-pypi` job is triggered only if the pushed branch starts with `refs/heads/main`. This job follows the same steps as `deploy-test-pypi`, but the distributions are published to PyPI instead of TestPyPI. The `password` to access PyPI is stored as a secret named `PYPI_API_TOKEN`.

Note: The code uses the `pypa/build` package for building the binary wheel and source tarball, and the `pypa/gh-action-pypi-publish@release/v1` Github Action for publishing the distributions to PyPI and TestPyPI.

## Unit Tests Workflow
This workflow is used to run unit tests on the OpenBB Terminal. The workflow is triggered on the following events:
The events this workflow will respond to are:

1.  Pull requests that are opened, synchronized, edited, or closed. The pull request must be made to the `develop` or `main` branches.

2.  Pushes to the `release/*` branches.

Each job in the workflow specifies a set of steps that are executed in order.

The first job, `check-files-changed`, checks whether there are any changes to certain file types in the repository, such as Python files and lockfiles. If there are changes, then the `check-changes` output variable is set to `true`.

The next job, `base-test`, runs a series of tests if `check-changes` is `true` and the base branch of the pull request is `develop`. This job sets up a Python 3.9 environment, installs Poetry, and then runs tests using `pytest`. Finally, it starts the terminal and exits.

The next job, `tests-python`, runs tests for different versions of Python (3.8, 3.9, and 3.10) on the `ubuntu-latest` operating system. It sets up the specified Python version, installs Poetry and dependencies, and then runs tests using `pytest`.

The next job, `full-test`, uses the GitHub Actions `checkout` action to checkout the code, followed by the `setup-python` action to set up the specified version of Python. Then, the `install-poetry` action is used to install the package manager Poetry, and a cache is set up using the `actions/cache` action to avoid re-installing dependencies. After that, the dependencies are installed using Poetry, and a list of installed packages is displayed. Then, the tests are run using `pytest`, and finally, the `terminal.py` script is started and exited.

The last job, `tests-conda`, sets up a Miniconda environment using the `setup-miniconda` action. The environment is specified using a YAML file and is activated. Then, the tests are run.

## Windows 10 Build Workflow
This is a GitHub Actions workflow file that automates the build and testing process for the OpenBB Terminal on Windows 10. The workflow consists of two jobs:

1.  Windows-Build
2.  Build-Exe

-   The Windows-Build job does the following:
    -   Sets up the Windows Git configuration for long file paths.
    -   Checks out the repository code.
    -   Sets up Python 3.9 and creates an OpenBB environment using poetry.
    -   Installs necessary packages and builds the terminal using PyInstaller.
    -   Uploads the built artifact to GitHub as an artifact.
-   The Build-Exe job does the following:
    -   Sets up the Windows Git configuration for long file paths.
    -   Checks out the repository code.
    -   Downloads the built artifact from the previous Windows-Build job.
    -   Copies the files into an app folder for building the EXE file.
    -   Builds the EXE file using NSIS.
    -   Uploads the built EXE as an artifact to GitHub.
    -   Runs integration tests on the terminal and saves the results to a text file.
    -   Uploads the test results summary to Slack.
    -   Cleans up previous build files and artifacts.

This workflow is triggered by the `workflow_dispatch` event and runs in concurrency with other workflows in the same group, with the ability to cancel in-progress builds. The concurrency group is defined as `${{ github.workflow }}-${{ github.ref }}`.
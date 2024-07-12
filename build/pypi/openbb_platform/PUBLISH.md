# Publishing to PyPI

## Pre-release

> [!WARNING]
> The `release` branch is solely for the purpose of publishing the package(s)! Any last minute changes should be made in appropriate PRs and merged to the `develop` branch. Once the `release` branch is created, the `develop` branch should be frozen for further commits until this process finishes.

> A `release` branch for a particular package should only cater to the changes for that package directory. For e.g. the `release/openbb-core-2.0.0` branch should only contain changes for the `openbb-core` package i.e. in the `openbb_platform/core` directory.

0. Merge `main` into `develop` and solve any conflict. You can do this by checking out `develop`, creating a branch `feature/merge-main-into-develop` and running `git merge main`. Merge this into `develop` if there are changes to commit.
1. Open a PR with the changes to be published in the format `release/<version>` (for e.g. `release/4.0.0` ). For a particular package use the format `release/<package>-<version>` (for e.g. `release/openbb-core-1.0.1`).
2. Bump `openbb` package version in `openbb_platform/pyproject.toml`.

> [!WARNING]
> The version must be incremented before running the tests in  4. and 5., since there are tests that rely of this to check for deprecated endpoints. Pay attention to commands that should be deprecated in the version you will publish.

3. Ensure all the CI workflows pass.
4. Ensure all unit tests pass: `pytest openbb_platform -m "not integration"`
5. Ensure all integration tests pass: `pytest openbb_platform -m integration`

## Release

> Ensure you have the appropriate credentials and permissions to publish to PyPI.

1. Run the following commands for publishing the packages to PyPI:

    > [!TIP]
    > Consider using the `--dry-run` flag to check if everything is correct before publishing.

    > For a single package release (e.g. patching `openbb-core`), the following steps are not required since the package can be published manually.

    1. To publish `openbb-core` run: `python build/pypi/openbb_platform/publish.py --core`
    2. To publish **ALL** extensions run: `python build/pypi/openbb_platform/publish.py --extensions`
    3. To publish `openbb` (the main package) run: `python build/pypi/openbb_platform/publish.py --openbb`
    > [!TIP]
    > Note that, in order for packages to pick up the latest versions of dependencies, it is advised to clear the local cache of the dependencies: we can do that with `pip cache purge` and `poetry cache clear pypi --all`. Sometimes there might be some delay in the PyPI API, so it might be necessary to wait a few minutes for pip to pick the latest versions.

2. Publish the CLI

    2.1. Bump `openbb` dependency on `cli/pyproject.toml` to the latest version

    2.2. Run `poetry publish --build` from `cli`

3. Regenerate assets for external use by running `python assets/scripts/generate_extension_data.py`.
4. Merge `release/<package>-<version>` to the `main` branch.
5. Run `Deploy to GitHub Pages` action in [openbb-docs](https://github.com/OpenBB-finance/openbb-docs/actions) to update the documentation website. Go to [docs.openbb.co](https://docs.openbb.co) to see the changes.

## Post-release

1. Install the packages on Google Colaboratory via PyPi and test to check if everything is working as expected.
2. Install the packages in a new environment locally via PyPi and test to check if everything is working as expected.
3. Open a new PR with the `release/<package>-<version>` branch pointing to the `develop` branch.
4. Merge the `release/<package>-<version>` branch to the `develop` branch.
5. If any bugs are encountered, create a new branch - `hotfix` for `main` and `bugfix` for `develop` and merge them accordingly.

### Generate the changelog

1. Run the changelog automation by using the "release_drafter" GitHub action and input the number of the last release PR (not this one!).
2. Edit and make the changelog live on the repository.
3. Paste it in the platform-release-changelog Slack channel.

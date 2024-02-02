# Publishing to PyPI

Publishing checklist:

> Note: you need to have the appropriate credentials and permissions to publish to PyPI

1. Ensure all unit tests pass: `pytest openbb_platform -m "not integration"`
2. Ensure all integration tests pass: `pytest openbb_platform -m integration`
3. Run `python -c "import openbb; openbb.build()"` to build the static assets. Make sure that only required extensions are installed.

    > **Note** Run `python -c "import openbb"` after building the static to check that no additional static is being built.

4. Run the following commands for publishing the packages to PyPI:

    Consider using the `--dry-run` flag to check if everything is correct before publishing.
    Also, it might be a good idea to run the script in batches to ensure that the packages are published correctly and the dependencies pick the correct versions.

    1. For the core package run: `python build/pypi/openbb_platform/publish.py --core`
    2. For the extension and provider packages run: `python build/pypi/openbb_platform/publish.py --extensions`
    3. For the `openbb` package - **which requires manual publishing** - do the following
         - Bump the dependency package versions
         - Re-build the static assets that are bundled with the package
         - Run unit tests to validate the existence of deprecated endpoints

    > [!TIP]
    > Note that, in order for packages to pick up the latest versions of dependencies, it is advised to clear the local cache of the dependencies:
    >
    > We can do that with `pip cache purge` and `poetry cache clear pypi --all`
    >
    > Also, sometimes there might be some delay in the PyPI API, so it might be necessary to wait a few minutes before publishing the next package.

5. Update poetry files: `python build/pypi/openbb_platform/poetry_update.py`
6. Open a PR so that changes are reflected on the main branch

Finally, check if everything works:

1. Install and test the package from Pypi on a clean environment.
2. Check if all the `pyproject.toml` files are correct, including the `openbb_platform` one.
3. Double check if there is any new extension or provider that needs to be added to [integration tests GitHub Action workflow](/.github/workflows/platform-api-integration-test.yml).

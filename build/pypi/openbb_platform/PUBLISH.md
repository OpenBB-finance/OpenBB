# Publishing to PyPI

Publishing checklist:

> Note: you need to have the appropriate credentials and permissions to publish to PyPI

1. Ensure all unit tests pass: `pytest openbb_platform -m "not integration"`
2. Ensure all integration tests pass: `pytest openbb_platform -m integration`
3. Run the publishing script: `python build/pypi/openbb_platform/publish.py`

    Consider using the `--dry-run` flag to check if everything is correct before publishing.
    Also, it might be a good idea to run the script in batches to ensure that the packages are published correctly and the dependencies pick the correct versions.
    Example, the extension packages need to pick the latest `openbb-core` version.
    Suggested batch order:
    1. Batch 1. Core
       1. `openbb-core`
    2. Batch 2. Extensions
       1. `openbb-charting`
       2. `openbb-crypto`
       3. `openbb-currency`
       4. ...
    3. Batch 3. Toolkits
       1. `openbb-quantitative`
       2. `openbb-technical`
       3. `openbb-econometrics`
       4. ...
    4. Batch 4. Providers
       1. `openbb-alpha-vantage`
       2. `openbb-benzinga`
       3. `openbb-biztoc`
       4. ...
    5. Batch 5. The meta-packages
       1. `openbb`
            When publishing this package:
            - Bump the dependency package versions
            - Re-build the static assets that are bundled with the package

    > Note that, in order for packages to pick up the latest versions of dependencies, it might be necessary to clear the local cache of the dependencies:
    >
    > We can do that with `pip cache purge` and `poetry cache clear pypi --all`
    >
    > Also, sometimes there might be some delay in the PyPI API, so it might be necessary to wait a few minutes before publishing the next package.

4. Update poetry files: `python build/pypi/openbb_platform/poetry_update.py`
5. Open a PR so that changes are reflected on the main branch

Finally, check if everything works:

1. Install and test the package from Pypi on a clean environment.
2. Check if all the `pyproject.toml` files are correct, including the `openbb_platform` one.
3. Double check if there is any new extension or provider that needs to be added to [integration tests GitHub Action workflow](/.github/workflows/platform-api-integration-test.yml).

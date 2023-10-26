# Publishing to PyPI

Publishing checklist:

> Note: you need to have the appropriate credentials and permissions to publish to PyPI

1. Ensure all unit tests pass: `pytest openbb_platform -m "not integration"`
2. Ensure all integration tests pass: `pytest openbb_platform -m integration`
3. Change the Platform version on:
   - `openbb_platform/platform/core/openbb_core/app/constants.py`
   - `openbb_platform/README.md`
4. Run the publishing script: `python openbb_platform/dev_utils/dev_publish.py`
5. Update poetry files: `python openbb_platform/dev_utils/poetry_update.py`
6. Open a PR so that changes are reflected on the main branch
7. If applicable, set the version on `constants.py` to use the `dev` tag again

Finally, check if everything workesd:

1. Install and test the package from Pypi on a clean environment
2. Check if all the `pyproject.toml` files are correct, including the `openbb_platform` one.
3. Double check if there is any new extension or provider that needs to be added to [integration tests GitHub Action workflow](/.github/workflows/platform-api-integration-test.yml).

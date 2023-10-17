# Publishing to PyPI

Publishing checklist:

> Note: you need to have the appropriate credentials and permissions to publish to PyPI

1. Ensure all unit tests pass: `pytest openbb_platform -m "not integration"`
2. Ensure all integration tests pass: `pytest openbb_platform -m integration`
3. Change the Platform version on `openbb_platform/platform/core/openbb_core/app/constants.py`
4. Run the publishing script: `python openbb_platform/dev_publish.py`
5. Update poetry files: `python openbb_platform/poetry_update.py`
6. Open a PR so that changes are reflected on the main branch

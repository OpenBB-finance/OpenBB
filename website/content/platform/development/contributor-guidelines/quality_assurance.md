---
title: Quality Assurance
sidebar_position: 2
description: This section provides an in-depth look at the Quality Assurance (QA) process in the OpenBB Platform. It covers the use of QA tools for testing extensions, creation of unit and integration tests, and the importance of maintaining a short import time for the package.
keywords:
- OpenBB QA process
- Unit and integration tests
- QA tools
- Extension testing
- Import time optimization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Quality Assurance - Contributor Guidelines - Development | OpenBB Platform Docs" />

We are strong believers in the Quality Assurance (QA) process and we want to make sure that all the extensions that are added to the OpenBB Platform are of high quality. To ensure this, we have a set of QA tools that you can use to test your extension.

Primarily, we have tools that semi-automate the creation of unit and integration tests.

> The QA tools are still in development and we are constantly improving them.

## Unit tests

Each `Fetcher` comes equipped with a `test` method that will ensure that it is implemented correctly and that it is returning the expected data. It also ensures that all types are correct and that the data is valid.

To create unit tests for your Fetchers, you can run the following command:

```bash
python openbb_platform/providers/tests/utils/unit_tests_generator.py
```

> Note that you should be running this file from the root of the repository.
> Note that the `tests` folder must exist in order to generate the tests.

The automatic unit test generation will add unit tests for all the fetchers available in a given provider.

To record the unit tests, you can run the following command:

```bash
pytest <path_to_the_unit_test_file> --record=all
```

> Note that sometimes manual intervention is needed. For example, adjusting out-of-top level imports or adding specific arguments for a given fetcher.

## Integration tests

The integration tests are a bit more complex than the unit tests, as we want to test both the Python interface and the API interface. For this, we have two scripts that will help you generate the integration tests.

To generate the integration tests for the Python interface, you can run the following command:

```bash
python openbb_platform/extensions/tests/utils/integration_tests_generator.py
```

To generate the integration tests for the API interface, you can run the following command:

```bash
python openbb_platform/extensions/tests/utils/integration_tests_api_generator.py
```

When testing the API interface, you'll need to run the OpenBB Platform locally before running the tests. To do so, you can run the following command:

```bash
uvicorn openbb_platform.platform.core.openbb_core.api.rest_api:app --host 0.0.0.0 --port 8000 --reload
```

These automated tests are a great way to reduce the amount of code you need to write, but they are not a replacement for manual testing and might require tweaking. That's why we have unit tests that test the generated integration tests to ensure they cover all providers and parameters.

To run the tests we can do:

- Unit tests only:

```bash
pytest openbb_platform -m "not integration"
```

- Integration tests only:

```bash
pytest openbb_platform -m integration
```

- Both integration and unit tests:

```bash
pytest openbb_platform
```

## Import time

We aim to have a short import time for the package. To measure that we use `tuna`.

- <https://pypi.org/project/tuna/>

To visualize the import time breakdown by module and find potential bottlenecks, run the
following commands from `openbb_platform` directory:

```bash
pip install tuna
python -X importtime openbb/__init__.py 2> import.log
tuna import.log
```

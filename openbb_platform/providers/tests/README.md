# Providers unit tests

In order to automatically generate unit tests for the providers you can run the following command:

```bash
python openbb_platform/providers/tests/utils/unit_test_generator.py
```

> Note that you should be running this file from the root of the repository.

The automatic unit test generation will add unit tests for all the fetchers available in a given provider.
Each provider will have one auto generated unit test file, and inside that file there will be one unit test for each fetcher.
If the fetcher was added at a later stage compared with the generation of the test file, one can run the script again and new fetchers only will be added.

> Note that sometimes manual intervention can be needed, for example, adjusting out-of-top level imports or adding specific arguments for a given fetcher.

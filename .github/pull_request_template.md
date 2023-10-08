# Pull Request OpenBB

## The OpenBBTerminal

<details>
<summary> Pull Request the OpenBBTerminal</summary>

### Description

- [ ] Summary of the change/ bug fix.
- [ ] Link # issue, if applicable.
- [ ] Screenshot of the feature or the bug before/after fix, if applicable.
- [ ] Relevant motivation and context.
- [ ] List any dependencies that are required for this change.

### How has this been tested?

- Please describe the tests that you ran to verify your changes.
- Provide instructions so we can reproduce.
- Please also list any relevant details for your test configuration.

- [ ] Make sure affected commands still run in terminal
- [ ] Ensure the SDK still works
- [ ] Check any related reports

### Checklist


- [ ] I have performed a self-review of my own code.
- [ ] I have commented my code, particularly in hard-to-understand areas.
- [ ] I have adhered to the GitFlow naming convention and my branch name is in the format of `feature/feature-name` or `hotfix/hotfix-name`.
- [ ] Update [our documentation](https://openbb-finance.github.io/OpenBBTerminal/) following [these guidelines](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/website).  Update any user guides that are affected by the changes.
- [ ] Update our tests following [these guidelines](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/tests).
- [ ] Make sure you are following our [CONTRIBUTING guidelines](https://github.com/OpenBB-finance/OpenBBTerminal/blob/main/CONTRIBUTING.md).
- [ ] If a feature was added make sure to add it to the corresponding [integration test script](https://github.com/OpenBB-finance/OpenBBTerminal/tree/develop/openbb_terminal/miscellaneous/integration_tests_scripts).

</details>

## The OpenBB Platform

<details>
<summary> Pull Request the OpenBB Platform</summary>

### Description

- [ ] Summary of the change/ bug fix.
- [ ] Link # issue, if applicable.
- [ ] Screenshot of the feature or the bug before/after fix, if applicable.
- [ ] Relevant motivation and context.
- [ ] List any dependencies that are required for this change.

### How has this been tested?

- Please describe the tests that you ran to verify your changes.
- Provide instructions so we can reproduce.
- Please also list any relevant details for your test configuration.

- [ ] Make sure all unit and integration tests pass
- If you changed a command or added a new one:
  - [ ] Make sure affected commands run and the output is correct
    - [ ] API
    - [ ] Python Interface
  - [ ] If applicable, add new tests for the command (see [CONTRIBUTING.md](/openbb_platform/CONTRIBUTING.md) to leverage semi-automated testing)
- If a new provider was added or a new fetcher was added to an existing provider:
  - [ ] Make sure existing tests pass
  - [ ] Make sure you can use the new provider and/or fetcher
  - [ ] If applicable, add new tests for the provider and/or fetcher (see [CONTRIBUTING.md](/openbb_platform/CONTRIBUTING.md) to leverage semi-automated testing)


### Checklist

- [ ] I have performed a self-review of my own code.
- [ ] I have commented my code, particularly in hard-to-understand areas.
- [ ] I have adhered to the GitFlow naming convention and my branch name is in the format of `feature/feature-name` or `hotfix/hotfix-name`.
- [ ] Make sure you are following our [CONTRIBUTING guidelines](https://github.com/OpenBB-finance/OpenBBTerminal/blob/main/CONTRIBUTING.md).
  - [ ] If applicable, update tests following [these guidelines](/openbb_platform/CONTRIBUTING.md#qa-your-extension).


</details>

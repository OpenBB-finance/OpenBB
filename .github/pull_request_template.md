# Pull Request OpenBB

## The OpenBBTerminal

<details>
<summary> Pull Request for the OpenBBTerminal</summary>

### Description

- [ ] Summary of the change/ bug fix.
- [ ] Link # issue, if applicable.
- [ ] Screenshot of the feature or the bug before/after fix, if applicable.
- [ ] Relevant motivation and context.
- [ ] List any dependencies that are required for this change.

### How has this been tested?

- Please describe the tests that you ran to verify your changes.
- Please provide instructions so we can reproduce.
- Please also list any relevant details for your test configuration.

- [ ] Ensure the affected commands still execute in the OpenBB Terminal.
- [ ] Ensure the Platform (previously named SDK) is working as intended.
- [ ] Check any related reports.

### Checklist

- [ ] I ensure I have self-reviewed my code.
- [ ] I have commented/documented my code, particularly in hard-to-understand sections.
- [ ] I have adhered to the GitFlow naming convention and my branch name is in the format of `feature/feature-name` or `hotfix/hotfix-name`.
- [ ] Update [our documentation](https://openbb-finance.github.io/OpenBBTerminal/) following [these guidelines](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/website).  Update any user guides that are affected by the changes.
- [ ] Update our tests following [these guidelines](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/tests).
- [ ] Make sure you are following our [CONTRIBUTING guidelines](https://github.com/OpenBB-finance/OpenBBTerminal/blob/main/CONTRIBUTING.md).
- [ ] If a feature was added make sure to add it to the corresponding [integration test script](https://github.com/OpenBB-finance/OpenBBTerminal/tree/develop/openbb_terminal/miscellaneous/integration_tests_scripts).

</details>

## The OpenBB Platform

<details>
<summary> Pull Request for the OpenBB Platform</summary>

### Description

- [ ] Summary of the change/ bug fix.
- [ ] Link # issue, if applicable.
- [ ] Screenshot of the feature or the bug before/after fix, if applicable.
- [ ] Relevant motivation and context.
- [ ] List any dependencies that are required for this change.

### How has this been tested?

- Please describe the tests that you ran to verify your changes.
- Please provide instructions so we can reproduce.
- Please also list any relevant details for your test configuration.

- [ ] Ensure all unit and integration tests pass.
- If you modified/added command(s):
  - [ ] Ensure the command(s) execute with the expected output.
    - [ ] API.
    - [ ] Python Interface.
  - [ ] If applicable, please add new tests for the command (see [CONTRIBUTING.md](/openbb_platform/CONTRIBUTING.md) to leverage semi-automated testing).
- If a new provider was introduced or a new fetcher was added to an existing provider:
  - [ ] Ensure the existing tests pass.
  - [ ] Ensure the new provider and/or fetcher is stable and usable.
  - [ ] If applicable, please add new tests for the provider and/or fetcher (see [CONTRIBUTING.md](/openbb_platform/CONTRIBUTING.md) to leverage semi-automated testing).
- If a new provider or extension was added:
  - [ ] Update the list of [Extensions](/openbb_platform/EXTENSIONS.md).
  - [ ] Update the list of [Providers](/openbb_platform/PROVIDERS.md).
  - [ ] If it's a community extension or provider, update the [integration tests GitHub Action workflow](/.github/workflows/platform-api-integration-test.yml).

### Checklist

- [ ] I have performed a self-review of my own code.
- [ ] I have commented my code, particularly in hard-to-understand areas.
- [ ] I have adhered to the GitFlow naming convention and my branch name is in the format of `feature/feature-name` or `hotfix/hotfix-name`.
- [ ] I ensure that I am following th [CONTRIBUTING guidelines](https://github.com/OpenBB-finance/OpenBBTerminal/blob/main/CONTRIBUTING.md).
  - [ ] (If applicable) I have updated tests following [these guidelines](/openbb_platform/CONTRIBUTING.md#qa-your-extension).

</details>

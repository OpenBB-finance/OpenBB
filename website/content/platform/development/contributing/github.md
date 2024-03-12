---
title: GitHub
sidebar_position: 5
description: This page outlines the GitHub branch naming conventions and information related to creating a pull request.
keywords:
- Commit changes
- PR creation
- Branch naming conventions
- Commit guidelines
- GitHub
- contributing
- submission
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="GitHub - Contributor Guidelines - Development | OpenBB Platform Docs" />

## Branch Naming Conventions

Before creating a new branch, switch to the `develop` branch and update your local cloned repo.

```console
git fetch
git checkout develop
```

If there are conflicting changes with the develop branch, `stash` the local changes first.

To submit a PR, a local branch or fork must be named according to the naming conventions:

- `feature/feature-name`
- `bugfix/bugfix-name`
- `docs/docs-name`

These branches can only have PRs pointing to the `develop` branch.

## Create Pull Request

A pull request should contain descriptions and details of all proposed changes, with any details maintainers and testers will need to know.
Please use one of the supplied Pull Request Templates.

Linting errors should be cleared, and any tests related to the changed files should be passing.

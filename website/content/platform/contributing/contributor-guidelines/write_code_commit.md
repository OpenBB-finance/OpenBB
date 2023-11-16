---
title: Write Code and Commit
sidebar_position: 5
description: This guide provides detailed instructions on how to write code and commit changes for the OpenBB Platform. It covers the process of creating a PR, branch naming conventions, and important guidelines to follow when committing changes.
keywords:
- OpenBB code writing
- Commit changes
- PR creation
- Branch naming conventions
- Commit guidelines
- GitHub
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Write Code and Commit - Contributor Guidelines - Contributing | OpenBB Platform Docs" />

## How to create a PR?

To create a PR to the OpenBB Platform, you'll need to fork the repository and create a new branch.

1. Create your Feature Branch, e.g. `git checkout -b feature/AmazingFeature`
2. Check the files you have touched using `git status`
3. Stage the files you want to commit, e.g.
   `git add openbb_platform/platform/core/openbb_core/app/constants.py`.
   Note: **DON'T** add any files with personal information.
4. Write a concise commit message under 50 characters, e.g. `git commit -m "meaningful commit message"`. If your PR
   solves an issue raised by a user, you may specify such issue by adding #ISSUE_NUMBER to the commit message, so that
   these get linked. Note: If you installed pre-commit hooks and one of the formatters re-formats your code, you'll need
   to go back to step 3 to add these.

### Branch Naming Conventions

The accepted branch naming conventions are:

- `feature/feature-name`
- `hotfix/hotfix-name`

These branches can only have PRs pointing to the `develop` branch.

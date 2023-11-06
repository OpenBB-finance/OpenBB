---
title: Create a Pull Request
sidebar_position: 5
description: Learn how to create a Pull Request to the OpenBB Platform, including
  steps like creating a feature branch, staging files, writing commit messages, and
  more. Also learn about the installation of pre-commit hooks and the conventions
  for branch naming.
keywords:
- OpenBB Platform
- Pull Request
- branch
- fork repository
- feature branch
- git status
- git add
- commit message
- pre-commit hooks
- branch naming conventions
- develop branch
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Create a Pull Request - Platform Development - Contributing | OpenBB Platform Docs" />

To create a Pull Request to the OpenBB Platform, you'll need to fork the repository and create a new branch.

1. Create your Feature Branch, e.g. `git checkout -b feature/AmazingFeature`
2. Check the files you have touched using `git status`
3. Stage the files you want to commit, e.g.
   `git add openbb_terminal/stocks/stocks_controller.py openbb_terminal/stocks/stocks_helper.py`.
   Note: **DON'T** add any files with personal information.
4. Write a concise commit message under 50 characters, e.g. `git commit -m "meaningful commit message"`. If your PR
   solves an issue raised by a user, you may specify such issue by adding #ISSUE_NUMBER to the commit message, so that
   these get linked. Note: If you installed pre-commit hooks and one of the formatters re-formats your code, you'll need
   to go back to step 3 to add these.

## Install pre-commit hooks

To install pre-commit hooks, run `pre-commit install` in the root of the repository.

## Branch Naming Conventions

The accepted branch naming conventions are:

- `feature/feature-name`
- `hotfix/hotfix-name`

These branches can only have PRs pointing to the `develop` branch.

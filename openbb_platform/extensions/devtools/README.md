# The OpenBB DevTools Extension

This extension aggregates the dependencies that facilitate a nice development experience
for OpenBB. It does not contain any code itself, but rather pulls in the following dependencies:

- Linters (ruff, pylint, mypy)
- Code formatters (black)
- Code quality tools (bandit)
- Pre-commit hooks (pre-commit)
- CI/CD configuration (tox, pytest, pytest-cov)
- Jupyter kernel (ipykernel)
- ... add your productivity booster here ...

## Installation

The extension is included into the dev_install.py script.

Standalone installation:

```bash
pip install openbb-devtools
```

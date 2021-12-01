# Gamestonk Terminal Code Documentation

Requirements:

- sphinx
- myst_parser

The `requirements.txt` file that mentions `myst_parser` is needed for readthedocs.io to build the documentation automatically.

Usage:

In the `docs` folder execute:

```bash
rm -rf code && sphinx-apidoc ../gamestonk_terminal/ -o ./code
make html
```

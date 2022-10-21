# OpenBB Terminal Code Documentation

## Creating Hugo SDK Documentation

To generate markdown files for the Hugo website do the following:

1. Go to the openbb directory:`cd ~/OpenBBTerminal`
1. Generate the documentation: `python docs/generate.py`
1. Change into the website directory: `cd website`
1. Run the hugo server to confirm changes applied: `hugo server -D`

## Creating Sphinx Documentation

Requirements:

- sphinx
- myst_parser

The `requirements.txt` file that mentions `myst_parser` is needed for readthedocs.io to build the documentation automatically.

Usage:

In the `docs` folder execute:

```bash
rm -rf code && sphinx-apidoc ../openbb_terminal/ -o ./code
make html
```

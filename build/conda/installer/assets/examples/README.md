# Example Extension Templates

The extensions in this folder represent starting points for creating your own OpenBB extensions. The types of extensions that can be created are:

- Router
  - Create a new router path and define the functions for the app.
- Provider
  - Add a new data provider source.
- OBBject
  - Extend the response object returned by every command.

## Installation

### All Examples

To install all example extensions, activate the environment, then run:

```sh
python install_examples.py
```

### Individual Example

To install an individual extension to the existing OpenBB environment, activate it, then navigate into the folder of the desired extension and enter:

```sh
poetry install --only-root
```

Then, rebuild the OpenBB Python interface with:

```sh
openbb-build
```

The new extension(s) will be available by importing the OpenBB package.

```python
from openbb import obb
```

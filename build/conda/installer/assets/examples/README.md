# Example Extension Templates

The extensions in this folder represent starting points for creating your own OpenBB extensions.

## Installation

To install in the existing OpenBB environment, actiavte it, then navigate into the folder of the desired extension and enter:

```console
poetry install --only-root
```

Then, rebuild the OpenBB Python interface with:

```console
openbb-build
```

The new extension(s) will be available by importing the OpenBB package.

```python
from openbb import obb
```

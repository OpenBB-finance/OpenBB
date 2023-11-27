---
title: OBBject Extensions
sidebar_position: 9
description: This page provides information about how to write extensions for the OpenBB OBBject class.
keywords:
- OBBject
- Python
- Development
- OpenBB Platform
---

As mentioned, OpenBB provides some basic methods for interacting with common data structures that will be seen in the results attribute.
If you are working with custom data, or adding new endpoints, it is possible that you will want to have your own methods for interacting with the data.
The OpenBB Platform provides a way to do this by extending the OBBject class.
The architecture for extensions was designed similar to how extensions and accessors are done in pandas, and relies on plugins through the poetry dependency management package.

This page will go through the steps of developing a simple, custom extension for the OBBject class.

### Entry Point

In our extension, we create the `openbb_example` extension.  In the new folder, we create the `pyproject.toml` file with the usual setup and dependency information.  In the toml file, we will include the following block:
```toml
[tool.poetry.plugins."openbb_obbject_extension"]
example = "openbb_example:ext"
```

With this in the file, we can install the extension by running `poetry install` from the extension folder.

### Writing the extension

We provide a class for handling the extensions.  In your code, we define our extension class as follows:

```python
from openbb_core.app.model.extension import Extension
ext = Extension(name="example", credentials=["some_api_key"])
```

The credentials are required if the extension requires a key for data or a service, or it can alternatively be connection information for a database, or any other information that needs to be passed to the extension.

Now we define the extension functionality.  Here, we just add a method to say hi:


```python
@ext.obbject_accessor
class Example:
    def __init__(self, obbject):
        self._obbject = obbject

    def hello(self):
        api_key = self._obbject._credentials.some_api_key
        print(f"Hello, this is my credential: {api_key}!")
```

### Using the extension

Now that the extension is installed and built, we can use it!  Because we are extending the `OBBject`, this will be available on any function:

```shell
>>> from openbb import obb
>>> obbject = obb.equity.price.historical("AAPL")
>>> obbject.example.hello()
Hello, this is my credential: None!
```

IN this example, we have added obbject.example as the extension and can use the .hello() functionality right from our OBBject.

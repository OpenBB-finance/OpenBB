# OpenBB ODP Extensions Cookiecutter

[Cookiecutter](https://cookiecutter.readthedocs.io/en/1.7.2/) is a command-line utility that creates projects from templates.

This extension is a simple template for setting up new OpenBB Python Package extensions and projects.

## Template Structure

The Cookiecutter template prompts the user for information to use in the `pyproject.toml` file, and then generates a project based on that information.
All fields are optional.

- Your Name
- Your Email
- Project Name
- Project Tag (some-distributable-package)
- Package Name ("include" code folder name - "some_package")
- Provider Name - name of the provider for the entry point - i.e, 'fmp'
- Router Name - name of the router path - i.e. `obb.{some_package}`
- OBBject Name - name of the OBBject accessor namespace.

The template will generate all extension types as a single, installable Python project.
You likely won't always use all in tandem, just delete the unwanted folders and entrypoints.

## Usage

1. Install in a Python environment from PyPI with:

```
pip install openbb-cookiecutter
```

Alternatively, with `uvx`:

```
uvx openbb-cookiecutter
```

2. Navigate the current working directory to the desired output location and run:

```
openbb-cookiecutter
```

Enter values or press `enter` to continue with the default.

3. Create a new Python environment for the project.

4. Navigate into the generated folder and install with:

```
pip install -e .
```

5. Python static files will be generated on first import, or trigger with `openbb-build`.

6. Import the Python package or start the API and use like any other OpenBB application.

7. Modify the business logic and get started building!

See the developer documentation [here](https://docs.openbb.co/python/developer).

## Contributing

We welcome contributions to this template! Please feel free to open an issue or submit a pull request with your improvements.

## Contacts

If you have any questions about the cookiecutter or anything OpenBB, feel free to email us at `support@openbb.co`

If you want to say hi, or are interested in partnering with us, feel free to reach us at `hello@openbb.co`

Any of our social media platforms: [openbb.co/links](https://openbb.co/links)

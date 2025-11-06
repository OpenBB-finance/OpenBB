# OpenBB ODP Extensions Cookiecutter Template

## Introduction

This is the generated cookiecutter template for the OpenBB Python Package.
It is used to help you create a new extension that can be integrated into the existing structure

With it you can:

- Create a new extension
- Build custom commands
- Interact with the standardization framework
- Build custom services and applications on top of the framework

## Getting Started

We recommend you check out the files in the following order:

* `{{cookiecutter.package_name}}/routers/{{cookiecutter.router_name}}.py`
* `{{cookiecutter.package_name}}/prvoviders/{{cookiecutter.provider_name}}/models/example.py`
* `{{cookiecutter.package_name}}/providers/{{cookiecutter.provider_name}}/__init__.py`
* `{{cookiecutter.package_name}}/obbject/{{cookiecutter.obbject_name}}/__init__.py`
* `{{cookiecutter.package_name}}/routers/{{cookiecutter.router_name}}_views.py`

Check out the developer [documentation](https://docs.openbb.co/python/developer) for more information on getting started making OpenBB extensions.

---

🦋 Made with [openbb cookiecutter](https://github.com/openbb-finance/OpenBB/cookiecutter).

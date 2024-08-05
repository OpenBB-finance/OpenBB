# OpenBB Platform Installation Package

The updater scripts for the OpenBB Platform updates the `lock` file when there are any changes to packages in the `pyproject` file.

The bash/cmd shortcuts provide a command line terminal shell with the Python environment and all items in the `bin/` folder on $PATH.
Use the shell profile when making changes or customizations to your installed environment and update the files accordingly.

1. Update `pyproject.toml`
  - Add/change packages to install.
2. Update `requirements.txt`
  - Make the same changes in this file.
3. Run the openbb-updater script (OpenBB Updater shortcut on Windows).

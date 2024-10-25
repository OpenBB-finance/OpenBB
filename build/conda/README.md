# OpenBB Platform Installer

The code in this folder creates a packaged installer for the OpenBB Platform, using Conda Constructor.

The installers can be created for Windows (.exe), MacOS (.pkg).

The installer is distributed with a Conda environment that contains Python and package management tools.

The dependencies required to run the application are installed from PyPI by the constructor's post_install script. They are installed by poetry and are defined in the `installer/assets/openbb_platform_installer/pyproject.toml` file.

The version of Python is defined in the `construct.yaml` file. It is set for 3.12.

## Build Instructions

**In order to build the installer, conda should be already installed and initialized your current shell profile.**

Navigate into the `build/conda` folder and then begin.

1. Create the Conda environment.
   - `conda env create --file environments/constructor.yml`
2. Activate the environment.
   - `conda activate constructor`
3. Build the installer.
   - `constructor installer/.`

## For when we have a full NSIS

To check nsis file - run

```batch
miniconda3\envs\constructor\NSIS\makensis.exe /V2 assets\installer.nsi
```

gives better output for errors

```batch
miniconda3\envs\constructor\NSIS\makensis.exe /V4 assets\installer.nsi
```

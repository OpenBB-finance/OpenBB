# OpenBB Platform Installer

The code in this folder creates a packaged installer for the OpenBB Platform, using Conda Constructor.

The installers can be created for Windows (.exe), MacOS (.pkg).

The installer is distributed with a Conda environment that contains Python and package management tools.

The dependencies required to run the application are installed from PyPI by the constructor's post_install script,
and are defined in the `requirements.txt` file.

The version of Python is defined in the `construct.yaml` file, it is set for 3.12.

**Conda should be installed already, and initialized in the current shell profile.**

# Build Instructions

Navigate into the `build/conda` folder and then begin.

1. Create the Conda environment.
    - `conda env create -n constructor --file environments/constructor.yml`
2. Activate the environment.
    - `conda activate constructor`
3. Build the installer.
    - `constructor installer/.`


# For when we have a full NSIS

To check nsis file - run

miniconda3\\envs\\constructor\\NSIS\\makensis.exe /V2 assets\\installer.nsi

gives better output

miniconda3\\envs\\constructor\\NSIS\\makensis.exe /V4 assets\\installer.nsi

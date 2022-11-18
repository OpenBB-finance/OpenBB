# TROUBLESHOOT

<!-- markdownlint-disable MD033 -->

If you are visiting this page it means that you're having issues installing. We deeply apologize for that.

Since the start of the project we've come across different types of issues experienced by the users. This page tries to combine issues, and their solutions.
This will allow to give the best install experience to everyone regardless of any programming skills.

<ol>
<li>
  <a href="#">Standard Install Troubles</a>
  <ul>
    <li><a href="#microsoft-visual-v++">Microsoft Visual C++</a></li>
    <li><a href="#wheel">Wheel</a></li>
    <li><a href="#Poetry">Poetry</a></li>
  </ul>
</li>
<li>
  <a href="#">ModuleNotFoundError Trouble</a>
  <ul>
    <li><a href="#general">General</a></li>
  </ul>
</li>
<li>
  <a href="#machine-learning-troubles">Machine Learning Troubles</a>
</li>
<li>
  <ul>
    <li><a href="#CRLF-versus-LF">CRLF versus LF</a></li>
  </ul>
</li>
</ol>

## Standard Install Troubles

### Microsoft Visual C++

If you are on Windows and your terminal has too many red error lines, it is likely that
this is the issue. Go to this page and install the 2019 Build Tools (not the latest):
<https://answers.microsoft.com/en-us/windows/forum/windows_other-windows_install/microsoft-visual-c-140/6f0726e2-6c32-4719-9fe5-aa68b5ad8e6d>

### Wheel

`conda install -c conda-forge wheel` or `pip install wheel`

### Poetry

If you get errors about .whl files not existing (usually on Windows) you have to reinitialize the following folder.
Just removing the 'artifacts' folder could also be enough:

| Platform | Location                        |
| -------- | ------------------------------- |
| Linux    | "~/.cache/pypoetry"             |
| Mac      | "~/Library/Caches/pypoetry"     |
| Windows  | "%localappdata%/pypoetry/cache" |

When you try to add a package to Poetry it is possible that it causes a similar issue. Here you can remove the
'artifacts' folder again to reinitialize Poetry.

If you run into trouble with Poetry, and the advice above did not help, your best bet is to try

1. `poetry update --lock`

2. `conda deactivate` -> `conda activate obb`, then try again

3. Track down the offensive package and purge it from your anaconda `<environment_name>` folder, then try again
   (removing through conda can sometimes leave locks behind)

   | Platform  | Location                                     |
   | --------- | -------------------------------------------- |
   | Linux/Mac | "~/anaconda3/envs" or "~/opt/anaconda3/envs" |
   | Windows   | "%userprofile%/anaconda3/envs"               |

4. Completely nuke your conda environment folder and make a new environment from scratch

5. Reboot your computer and try again

6. Submit a ticket on GitHub

#### JSONDecodeError during `poetry install`

Sometimes poetry can throw a `JSONDecodeError` on random packages while running `poetry install`.
This can be observed on macOS 10.14+ running python 3.8+.
This is because of the use of an experimental installer that can be switched off to avoid the mentioned error.
Run

```bash
poetry config experimental.new-installer false
```

as advised [here](https://github.com/python-poetry/poetry/issues/4210) and it should fix the installation process.

## ModuleNotFoundError Trouble

### General

In the case when you run into an error of the form `ModuleNotFoundError: No module named '_______'` before you start installing these modules that have not been found please check that you have most followed the recommended installation instructions.
These errors often can occur when you have not activated the virtual environment where you have installed the terminal, or you have not used the `poetry install` command to install the dependencies.

In case you wish to proceed with an alternative way to install the terminal feel free to install the missing packages via pip. For example if you get the error that `yfinance` is not found, you would run `pip install yfinance`

### Machine Learning Troubles

If you run into issues installing or `Cannot convert a symbolic Tensor...` at runtime, try this:

```bash
poetry install
poetry install -E prediction
```

_Commands that may help you in case of an error:_

- `python -m pip install --upgrade pip`
- `poetry update --lock`
- `poetry install`

### CRLF versus LF

When trying to commit code changes, pylint will prevent you from doing so if your line break settings are set to
CRLF (default for Windows).
This is because the entire package uses LF (default for Linux/Mac), and it is therefore
important that you change this setting to LF _before_ you make any changes to the code.

It is possible that CRLF automatically turns back on, you can correct this with:

```bash
git config --global core.autocrlf false
```

In case you already made coding adjustments, you have to reset your cache, and the changes you made to the code with
the following:

```bash
git rm --cached -r .
git reset --hard
```

### Unable to run openbb from VS Code integrated terminal

Occurs when vscode terminal python version/path is different from the terminal version.

To fix it add this to vscode JSON settings ([ref](https://stackoverflow.com/questions/54582361/vscode-terminal-shows-incorrect-python-version-and-path-launching-terminal-from)):

```bash
    "terminal.integrated.inheritEnv": false,
```

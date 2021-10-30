# TROUBLESHOOT

If you are visiting this page it means that you're having issues installing. We deeply apologize for that.

Since the start of the project we've come across different types of issues experienced by the users. This page tries to
combine issues, and their solutions. This will allow to give the best install experience to everyone regardless of any
programming skills.

<ol>
<li>
  <a href="#">Standard Install Troubles</a>
  <ul>
    <li><a href="#microsoft-visual-v++">Microsoft Visual C++</a></li>
    <li><a href="#wheel">Wheel</a></li>
    <li><a href="#cvxpy">Cvxpy</a></li>
    <li><a href="#numpy">Numpy</a></li>
    <li><a href="#Poetry">Poetry</a></li>
  </ul>
</li>
<li>
  <a href="#">ModuleNotFoundError Trouble</a>
  <ul>
    <li><a href="#general">General</a></li>
    <li><a href="#pypfopt">pypfopt</a></li>
    <li><a href="#dotenv">dotenv</a></li>
    <li><a href="#ally">ally</a></li>
  </ul>
</li>
<li>
  <a href="#machine-learning-troubles">Machine Learning Troubles</a>
</li>
<li>
  <a href="#other-issues">Other Issues</a>
  <ul>
    <li><a href="#CRLF-versus-LF">CRLF versus LF</a></li>
  </ul>
</li>
</ol>

## Standard Install Troubles

### Microsoft Visual C++

If your terminal has too many red error lines, it is likely that this is the issue. Go to this page and install the c++
build tools:
<https://answers.microsoft.com/en-us/windows/forum/windows_other-windows_install/microsoft-visual-c-140/6f0726e2-6c32-4719-9fe5-aa68b5ad8e6d>

### Wheel

`conda install -c conda-forge wheel` or `pip install wheel`

### Cvxpy

```bash
conda install -c conda-forge cvxpy
```

### Numpy

```bash
pip install --upgrade numpy==1.20.2
```

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

2. `conda deactivate` -> `conda activate gst`, then try again

3. Track down the offensive package and purge it from your anaconda `<environment_name>` folder, then try again
   (removing through conda can sometimes leave locks behind)

   | Platform  | Location                                     |
   | --------- | -------------------------------------------- |
   | Linux/Mac | "~/anaconda3/envs" or "~/opt/anaconda3/envs" |
   | Windows   | "%userprofile%/anaconda3/envs"               |

4. Completely nuke your conda environment folder and make a new environment from scratch

5. Reboot your computer and try again

6. Submit a ticket on GitHub

## ModuleNotFoundError Trouble

### General

In the case when you run into an error of the form `ModuleNotFoundError: No module named '_______'`. The solution is to
install the missing package via pip.

If you get the error that `yfinance` is not found, you would run

- `pip install yfinance`

Then please submit an issue so that we can address why that was not imported.

Please note that the package `pmdarima` needs to installed through `pip install` and not through `conda install`.

### pypfopt

```bash
pip install PyPortfolioOpt
```

### dotenv

```bash
pip install python-dotenv
```

### ally

```bash
pip install pyally
```

### Machine Learning Troubles

If you run into issues installing or `Cannot convert a symbolic Tensor...` at runtime, try this:

```bash
conda install -c conda-forge numpy=1.19.5 hdf5=1.10.5
poetry install
poetry install -E prediction
```

_Commands that may help you in case of an error:_

- `python -m pip install --upgrade pip`
- `pip install pystan --upgrade`
- `poetry update --lock`

## Other Issues

### CRLF versus LF

When trying to commit code changes, pylint will prevent you from doing so if your line break settings are set to
CRLF (default for Windows). This is because the entire package uses LF (default for Linux/Mac), and it is therefore
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

### Unable to run gst from VS Code integrated terminal

Occurs when vscode terminal python version/path is different from the terminal version.

To fix it add this to vscode JSON settings ([ref](https://stackoverflow.com/questions/54582361/vscode-terminal-shows-incorrect-python-version-and-path-launching-terminal-from)):

```bash
    "terminal.integrated.inheritEnv": false,
```

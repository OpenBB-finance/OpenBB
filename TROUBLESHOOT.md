
# TROUBLESHOOT

If you are visiting this page it means that you're having issues installing. We deeply apologize for that.

Since the start of the project we've come across different types of issues experienced by the users. This page tries to combine issues, and their solutions. This will allow to give the best install experience to everyone regardless of any programming skills.

<ol>
<li>
  <a href="#">Standard Install Troubles</a>
  <ul>
    <li><a href="#Microsoft-Visual-C++">Microsoft Visual C++</a></li>
    <li><a href="#wheel">Wheel</a></li>
    <li><a href="#cvxpy">Cvxpy</a></li>
    <li><a href="#numpy">Numpy</a></li>
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
</li>
</ol>


## Standard Install Troubles

### Microsoft Visual C++

If your terminal has too many red error lines, it is likely that this is the issue. Go to this page and install the c++ build tools:
https://answers.microsoft.com/en-us/windows/forum/windows_other-windows_install/microsoft-visual-c-140/6f0726e2-6c32-4719-9fe5-aa68b5ad8e6d


### Wheel

`conda install -c conda-forge wheel` or `pip install wheel`


### Cvxpy

```
conda install -c conda-forge cvxpy
```

### Numpy

```
pip install --upgrade numpy==1.20.2
```


## ModuleNotFoundError Trouble

### General

In the case when you run into an error of the form `ModuleNotFoundError: No module named '_______'`.  The solution is to
install the missing package via pip.

If you get the error that `yfinance` is not found, you would run
* `pip install yfinance`

Then please submit an issue so that we can address why that was not imported.

Please note that the package `pmdarima` needs to installed through `pip install` and not through `conda install`.

### pypfopt
```
pip install PyPortfolioOpt
```

### dotenv
```
pip install python-dotenv
```

### ally
```
pip install pyally
```


## Machine Learning Trouble

If you run into issues installing or `Cannot convert a symbolic Tensor...` at runtime, try this:

```
conda install -c conda-forge fbprophet numpy=1.19.5 hdf5=1.10.5
poetry install
poetry install -E prediction
```

*Commands that may help you in case of an error:*

* `python -m pip install --upgrade pip`
* `pip install pystan --upgrade`
* `poetry update --lock`


### Other Issues

If you run into trouble with poetry and the advice above did not help, your best bet is to try

1. `poetry update --lock`

2. `conda deactivate` -> `conda activate gst`, then try again

3. Delete the poetry cache, then try again

   | Platform | Location                        |
   | -------- | ------------------------------- |
   | Linux    | "~/.cache/pypoetry"             |
   | Mac      | "~/Library/Caches/pypoetry"     |
   | Windows  | "%localappdata%/pypoetry/cache" |

4. Track down the offensive package and purge it from your anaconda `<environment_name>` folder, then try again (removing through conda can sometimes leave locks behind)

   | Platform  | Location                                     |
   | --------- | -------------------------------------------- |
   | Linux/Mac | "~/anaconda3/envs" or "~/opt/anaconda3/envs" |
   | Windows   | "%userprofile%/anaconda3/envs"               |

5. Completely nuke your conda environment folder and make a new environment from scratch

6. Reboot your computer and try again

7. Submit a ticket on github

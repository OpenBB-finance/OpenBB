# REPORTS

This menu has a different concept from remaining menus. It has 2 main goals:

- Generate a personalised report.
- Allow the user to write notes on that notebook (report), as if it was his personal investment diary.

## How to create your own personal report

1. Copy one of the existing notebook reports as a template, e.g. [dark_pool.ipynb](/openbb_terminal/reports/dark_pool.ipynb).

2. Rename that notebook with a name that reflects what you want this notebook to contain, even including your name.

3. One of the notebook cells will have a `parameters` tag, that's where the papermill will parametrize the notebook.
   Thus, your variables should be declared there.

4. Remove the function calls that you don't care about to build your own report.

5. When building your template notebook, there are 2 type of possible things you can do:
   - Create a markdown cell, where you can add a title or a description. E.g.

   ```text
   ## Analyst Targets
   ```

   - Create a code cell, where you should both: import a module, and call a function to display a chart or print data. E.g.

   ```python
   from openbb_terminal.stocks.due_diligence import finviz_view

   finviz_view.analyst(ticker=ticker, export='')
   ```

**Note**: In order to find the name of the function you want, you should either crawl through the codebase (and ask
help in discord) or look into our readthedocs (#TODO).

## How to run the report

1. In [config_terminal](/openbb_terminal/config_terminal.py) you may need to change your `PAPERMILL_NOTEBOOK_REPORT_PORT`
   from `8888`. If the notebook generation fails, it is likely that the port selected is not the correct one.

2. Start the terminal with `python terminal.py`

3. Select `reports` context, and choose from the options selected - which are derived from the .ipynb jupyter notebook
   files on the [reports](/openbb_terminal/reports/) folder.

4. This should prompt you with a filled notebook with name: `<date time>_<report name>_<args>.ipynb`. E.g. `20210725_193517_dark_pool_AMC.ipynb`

5. Due to the last cell of the notebook, the report is saved by default as `.html`. E.g.  `20210725_193517_dark_pool_AMC.html`

   ```text
   folder = "notebooks/reports/"
   extension = ".ipynb"
   !jupyter nbconvert {report_name} --to html --no-input
   ```

6. You can now write your own personal notes on the notebook. By doing:
   - Click on the notebook cell that you are interested in writing your notes
   - On the toolbar click on "+" to add a new cell
   - On the toolbar click on "Cell" -> "Cell Type" -> "Markdown"
   - You're now ready to write your own notes

7. Once you're happy with your report, you can either:
   - Re-run the last cell, potentially changing output from `.html`:
   - Or, on the toolbar click on "File" -> "Download as" -> Select your preferred option (e.g. HTML)

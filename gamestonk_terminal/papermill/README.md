# PAPERMILL

This menu has a different concept from remaining menus. It has 2 main goals:
 - Generate a personalised report.
 - Allow the user to write notes on that notebook (report), as if it was his personal investment diary.

Command | Template | Example
------ | --------|----
`dd`   | [Due Diligence Template](/notebooks/templates/due_diligence.ipynb) | [Due Diligence Example](/notebooks/examples/aapl_due_diligence_20210729_001048.html)
`econ` | [Economy Template](/notebooks/templates/econ_data.ipynb) | [Economy Example](/notebooks/examples/econ_data_20210729_001227.html)
`dp` | [Dark Pool](/notebooks/templates/dark_pool.ipynb) | [Dark Pool](/notebooks/examples/amc_dark_pool_20210728_235316.html)
`cm` | [Crypto Market](/notebooks/templates/crypto_market.ipynb) | [Crypto Market](/notebooks/examples/crypto_market_20210729_001530.html)

     
## How to run the report

1. In [config_terminal](/gamestonk_terminal/config_terminal.py) you may need to change your `PAPERMILL_NOTEBOOK_REPORT_PORT` from `8888`. If the notebook generation fails, it is likely that the port selected is not the correct one.

2. Start the terminal with `python terminal.py`

3. Select `mill` and select one of the available reports generation, e.g. `econ`

4. This should prompt you with a filled notebok with name: `report_name_date_time.ipynb`. E.g. `econ_data_20210725_193517.ipynb`

5. Due to the last cell of the notebook, the report is saved by default as `.html`. E.g.  `econ_data_20210725_193517.html`
```
folder = "notebooks/reports/"
extension = ".ipynb"
!jupyter nbconvert {folder + report_name + extension} --to html --no-input
```

6. You can now write your own personal notes on the notebook. By doing:
   * Click on the notebook cell that you are interested in writing your notes
   * On the toolbar click on "+" to add a new cell
   * On the tooblar click on "Cell" -> "Cell Type" -> "Markdown"
   * You're now ready to write your own notes

6. Once you're happy with your report, you can either:
   * Re-run the last cell (potentially changing output from `.html` with: 
   ```
   folder = "notebooks/reports/"
   extension = ".ipynb"
   !jupyter nbconvert {folder + report_name + extension} --to html --no-input
   ```
   * Or, on the toolbar click on "File" -> "Download as" -> Select your preferred option (e.g. HTML)


# PAPERMILL

This menu has a different concept from remaining menus. It has 2 main goals:
 - Generate a personalised report.
 - Allow the user to write notes on that notebook (report), as if it was his personal investment diary.

Command | Template | Example
------ | --------|----
`dd`   | [Due Diligence Template](/notebooks/templates/due_diligence.ipynb) | [Due Diligence Example](/notebooks/examples/GME_20210704_191432_due_diligence.html)
`econ` | [Economy Template](/notebooks/templates/econ_data.ipynb) | [Economy Example](/notebooks/examples/econ_data_20210704_074122.html)

     
## How to run the report

1. In [config_terminal](/gamestonk_terminal/config_terminal.py) you may need to change your `PAPERMILL_NOTEBOOK_REPORT_PORT` from `8888`. If the notebook generation fails, it is likely that the port selected is not the correct one.

2. Start the terminal with `python terminal.py`

3. Select `mill` and select one of the available reports generation, e.g. `econ`

4. This should prompt you with a filled notebok with name: `report_name_date_time.ipynb`. E.g. `econ_data_20210725_193517.ipynb`

5. You can now write your own personal notes on the notebook. By doing:
   * Click on the notebook cell that you are interested in writing your notes
   * On the toolbar click on "+" to add a new cell
   * On the tooblar click on "Cell" -> "Cell Type" -> "Markdown"
   * You're now ready to write your own notes

6. Once you're happy with your report, you can export it by doing:
   * On the toolbar click on "File" -> "Download as" -> Select your preferred option (e.g. HTML)

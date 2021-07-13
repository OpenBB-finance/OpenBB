# PAPERMILL

This menu has a different concept from remaining menus. It has 2 main goals:
 - Generate a personalised report.
 - Allow the user to write notes on that notebook (report), as if it was his personal investment diary.

Command | Template | Example
------ | --------|----
`dd`   | [Due Diligence Template](/notebooks/templates/due_diligence.ipynb) | [Due Diligence Example](/notebooks/examples/GME_20210704_191432_due_diligence.html)
`econ` | [Economy Template](/notebooks/templates/econ_data.ipynb) | [Economy Example](/notebooks/examples/econ_data_20210704_074122.html)

     
## How to run the report

1. Before running the terminal, on the main directory "GamestonkTerminal" start a new notebook kernel with: `jupyter notebook`

2. Now you can start the terminal with `python terminal.py`

3. Select `mill` and select one of the available reports generation

4. This should prompt you with a filled notebok with name: `report_name_date_time.ipynb` 

5. You can now write your own personal notes on the notebook. By doing:
   * Click on the notebook cell that you are interested in writing your notes
   * On the toolbar click on "+" to add a new cell
   * On the tooblar click on "Cell" -> "Cell Type" -> "Markdown"
   * You're now ready to write your own notes

6. Once you're happy with your report, you can export it by doing:
   * On the toolbar click on "File" -> "Download as" -> Select your preferred option (e.g. HTML)

---
geekdocCollapseSection: true
---

{{< toc-tree >}}

# Loading in custom data

There is a directory in root, labeled `custom_imports`.  Here there is a sample
csv file titled `test.csv` that is __randomly__ generated data for visualization purposes.

When loading in the data, we recommend working with time series.  The prediction techniques menu
will plot against time data, so not using that may result in undesired outputs.

## How to load in a time variable

Note in the sample csv, the first row has the following form `Date,ColNorm,Col2,ColNorm3,ColB`.
The process for loading data into Gamestonk Terminal is that the code loops through all input columns and looks through
for one column that is either `Date`,`Time` or `Timestamp` (not case-sensitive).
If one of these are found, then the dataframe sets this column to be the index.

If onc of these columns are not found, then the index will just be integers from 0 to the length of your data.

Once again: __the prediction menu is designed for data with a datetime index__.
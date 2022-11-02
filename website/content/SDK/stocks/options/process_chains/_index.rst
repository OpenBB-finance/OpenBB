.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Function to take in the requests.get and return a DataFrame
    </h3>

{{< highlight python >}}
stocks.options.process_chains(
    response: requests.models.Response,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    response: *requests.models.Response*
        This is the response from tradier api.

* **Returns**

    opt_chain: *pd.DataFrame*
        Dataframe with all available options

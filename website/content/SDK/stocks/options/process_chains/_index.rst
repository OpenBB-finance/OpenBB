.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.options.process_chains(
    response: requests.models.Response,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Function to take in the requests.get and return a DataFrame
    </p>

* **Parameters**

    response: requests.models.Response
        This is the response from tradier api.

* **Returns**

    opt_chain: pd.DataFrame
        Dataframe with all available options

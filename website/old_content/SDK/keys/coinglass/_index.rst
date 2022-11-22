.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
keys.coinglass(
    key: str,
    persist: bool = False,
    show_output: bool = False,
    chart: bool = False,
) -> str
{{< /highlight >}}

.. raw:: html

    <p>
    Set Coinglass key.
    </p>

* **Parameters**

    key: str
        API key
    persist: bool
        If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool
        Display status string or not. By default, False.

* **Returns**

    status: str

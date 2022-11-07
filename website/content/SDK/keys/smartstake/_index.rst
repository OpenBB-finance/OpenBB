.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
keys.smartstake(
    key: str,
    access_token: str,
    persist: bool = False,
    show_output: bool = False,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Set Smartstake key.
    </p>

* **Parameters**

    key: str
        API key
    access_token: str
        API token
    persist: bool
        If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool
        Display status string or not. By default, False.

* **Returns**

    status: str

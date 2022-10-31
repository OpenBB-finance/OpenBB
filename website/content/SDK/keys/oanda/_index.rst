.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Set Oanda key
    </h3>

{{< highlight python >}}
keys.oanda(
    account: str,
    access_token: str,
    account_type: str = '',
    persist: bool = False,
    show_output: bool = False,
    ) -> str
{{< /highlight >}}

* **Parameters**

    account: *str*
        User account
    access_token: *str*
        User token
    account_type: *str*
        User account type
    persist: *bool*
        If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: *bool*
        Display status string or not. By default, False.

    
* **Returns**

    status: *str*
    
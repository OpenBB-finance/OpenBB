.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Set Robinhood key
    </h3>

{{< highlight python >}}
keys.rh(
    username: str,
    password: str,
    persist: bool = False,
    show\_output: bool = False,
    ) -> str
{{< /highlight >}}

* **Parameters**

    username: *str*
        User username
    password: *str*
        User password
    persist: *bool*
        If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show\_output: *bool*
        Display status string or not. By default, False.

    
* **Returns**

    status: *str*
    
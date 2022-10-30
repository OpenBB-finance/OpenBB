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
    access\_token: str,
    account\_type: str = '',
    persist: bool = False,
    show\_output: bool = False,
    ) -> str
{{< /highlight >}}

* **Parameters**

        account: *str*
            User account
        access\_token: *str*
            User token
        account\_type: *str*
            User account type
        persist: *bool*
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.
        show\_output: *bool*
            Display status string or not. By default, False.
    
* **Returns**

    status: *str*
    
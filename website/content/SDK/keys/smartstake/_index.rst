.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Set Smartstake key.
    </h3>

{{< highlight python >}}
keys.smartstake(
    key: str,
    access\_token: str,
    persist: bool = False,
    show\_output: bool = False,
    )
{{< /highlight >}}

* **Parameters**

    key: *str*
        API key
    access\_token: *str*
        API token
    persist: *bool*
        If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show\_output: *bool*
        Display status string or not. By default, False.

    
* **Returns**

    status: *str*
    
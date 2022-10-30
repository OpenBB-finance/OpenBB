.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Set Twitter key
    </h3>

{{< highlight python >}}
keys.twitter(
    key: str,
    secret: str,
    access_token: str,
    persist: bool = False,
    show_output: bool = False,
    ) -> str
{{< /highlight >}}

* **Parameters**

        key: *str*
            API key
        secret: *str*
            API secret
        access_token: *str*
            API token
        persist: *bool*
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.
        show_output: *bool*
            Display status string or not. By default, False.
    
* **Returns**

    status: *str*
    
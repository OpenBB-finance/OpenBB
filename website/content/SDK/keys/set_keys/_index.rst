.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Set API keys in bundle.
    </h3>

{{< highlight python >}}
keys.set_keys(
    keys\_dict: Dict[str, Dict[str, Union[str, bool]]],
    persist: bool = False,
    show\_output: bool = False,
    ) -> Dict
{{< /highlight >}}

* **Parameters**

    keys\_dict: Dict[str, Dict[str, Union[str, bool]]]
        E.g. {"fred": {"key":"XXXXX"}, "binance": {"key":"YYYYY", "secret":"ZZZZZ"}}
        More info on APIs can be found through get\_keys\_info().
    persist: *bool*
        If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show\_output: *bool*
        Display status string or not. By default, False.

    
* **Returns**

    status\_dict: *Dict*
    
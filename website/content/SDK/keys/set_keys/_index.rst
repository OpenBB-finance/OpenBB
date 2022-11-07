.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
keys.set_keys(
    keys_dict: Dict[str, Dict[str, Union[str, bool]]],
    persist: bool = False,
    show_output: bool = False,
    chart: bool = False,
) -> Dict
{{< /highlight >}}

.. raw:: html

    <p>
    Set API keys in bundle.
    </p>

* **Parameters**

    keys_dict: Dict[str, Dict[str, Union[str, bool]]]
        E.g. {"fred": {"key":"XXXXX"}, "binance": {"key":"YYYYY", "secret":"ZZZZZ"}}
        More info on APIs can be found through get_keys_info().
    persist: bool
        If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool
        Display status string or not. By default, False.

* **Returns**

    status_dict: Dict

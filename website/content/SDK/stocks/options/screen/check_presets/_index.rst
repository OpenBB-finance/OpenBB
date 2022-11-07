.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.options.screen.check_presets(
    preset_dict: dict,
    chart: bool = False,
) -> str
{{< /highlight >}}

.. raw:: html

    <p>
    Checks option screener preset values
    </p>

* **Parameters**

    preset_dict: dict
        Defined presets from configparser

* **Returns**

    error: str
        String of all errors accumulated

.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
keys.mykeys(
    show: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get currently set API keys.
    </p>

* **Parameters**

    show: bool
        Flag to choose whether to show actual keys or not.
        By default, False.

* **Returns**

    pd.DataFrame
        Currents keys

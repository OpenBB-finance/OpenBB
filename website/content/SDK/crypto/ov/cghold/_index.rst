.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns public companies that holds ethereum or bitcoin [Source: CoinGecko]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.ov.cghold(
    endpoint: str = 'bitcoin',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> List[Any]
{{< /highlight >}}

* **Parameters**

    endpoint : *str*
        "bitcoin" or "ethereum"
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    List:
        - str: *             Overall statistics*
        - pandas.DataFrame: *Companies holding crypto*

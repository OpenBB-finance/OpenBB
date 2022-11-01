.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Scrape all substack newsletters from url list.
    [Source: substack.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.newsletters(
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

etters from url list.
    [Source: substack.com]

    
* **Returns**

    pd.DataFrame
        DataFrame with recent news from most popular DeFi related newsletters.
    
.. role:: python(code)
    :language: python
    :class: highlight

|

> Get startups from ROSS index [Source: *https://runacap.com/]*
----------------------------------------------------------------
To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
alt.oss.ross(, chart = False) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**


    
* **Returns**

    pandas.DataFrame:
        list of startups
    
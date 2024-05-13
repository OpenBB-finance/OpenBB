---
title: Data slicer
sidebar_position: 2
description: Slice Excel ranges by label or index
keywords:
- Microsoft Excel
- Add-in
- Advanced
- Slice data
- Data slicer
- Get specific fields
---

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Data slicer | OpenBB Add-in for Excel Docs" />

To help you slice parts of data, we provide the [OBB.GET](https://docs.openbb.co/excel/reference/get) function. This function allows to slice rows, columns or range subsets. It is useful to extract specific fields from the `OBB.` custom functions. Data can be sliced by label or index.

### Example

- Suppose you called an `OBB.` function and it returned the following data at cells A1:D3:

| period_ending | revenue            | cost_of_revenue    | gross_profit       |
|---------------|--------------------|--------------------|--------------------|
| 2023/09/30    | 383 285 000 000.00 | 214 137 000 000.00 | 169 148 000 000.00 |
| 2022/09/24    | 394 328 000 000.00 | 223 546 000 000.00 | 170 782 000 000.00 |
| 2021/09/25    | 365 817 000 000.00 | 212 981 000 000.00 | 152 836 000 000.00 |

- Slicing a single row:

```excel
=OBB.GET(A1:D3,DATE(2023,9,30))
```

:::note
When passing date labels make sure to use the format `YYYY/MM/DD` or refer to a cell range containing Excel date format - DATE(year,month,day).
:::

- Slicing a single column:

```excel
=OBB.GET(A1:D3,,"revenue")
```

- Slicing by index:

```excel
=OBB.GET(A1:D3,2,3)
```

:::tip
To slice the from the last row use negative numbers. For example, `=OBB.GET(A1:D3,-1,-2)` will return the last row and the second to last column.
:::

- Slicing multiple rows and columns:

```excel
=OBB.GET(A1:D3,{"2023/09/30","2021/09/25"},{"cost_of_revenue","gross_profit"})
```

:::tip
The easiest way to pass ranges is to write them into cells and reference them in the function. For example, `=OBB.GET(...,A1:A2)` where A1 contains "item1", A2 "item2".
:::

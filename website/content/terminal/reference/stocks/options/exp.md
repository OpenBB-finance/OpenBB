---
title: exp
description: OpenBB Terminal Function
---

# exp

See and set expiration date

### Usage

```python
exp [-i {}] [-d {}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| index | Select index for expiry date. | -1 | True | range(0, 0) |
| date | Select date (YYYY-MM-DD) |  | True |  |


---

## Examples

```python
2022 Feb 16, 08:50 (🦋) /stocks/options/ $ exp

Available expiry dates:
    0.  2022-02-18
    1.  2022-02-25
    2.  2022-03-04
    3.  2022-03-11
    4.  2022-03-18
    5.  2022-03-25
    6.  2022-04-01
    7.  2022-04-14
    8.  2022-05-20
    9.  2022-06-17
   10.  2022-07-15
   11.  2022-08-19
   12.  2022-09-16
   13.  2022-10-21
   14.  2022-11-18
   15.  2022-12-16
   16.  2023-01-20
   17.  2023-03-17
   18.  2023-06-16
   19.  2023-09-15
   20.  2024-01-19

2022 Feb 16, 08:50 (🦋) /stocks/options/ $ exp 7
Expiration set to 2022-04-14
```
---

---
title: Fixed Income
description: This guide introduces the Fixed Income menu, in the OpenBB Terminal, and provides examples for use. Features in this menu cover reference rates and government bonds, as well as corporate bond indices.
keywords:
- Fixed Income
- Financial Terminal
- Rates and Indices
- Plotting Data
- Central Bank Rates
- Government Bonds
- Corporate Bonds
- Spreads
- API Key
- User Guide
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Fixed Income - Menus | OpenBB Terminal Docs" />

The Fixed Income menu functions for reference rates (ESTER, SOFR, SONIA and Ameribor), central bank rates (FRED, FOMC projections and ECB key interest rates), government bonds (treasury rates for any country, us-specific rates, yield curves), corporate bonds (ICE BofA Corporate Indices, Moody's AAA and BAA Corporate Indices, Commercial Paper, Spot Rates and HQM Corporate Yield Curve) and spreads (ICE BofA spreads, constant maturity spreads, and federal funds rate).

:::note

The menu relies on FRED for data requests, please refer to the [API keys guide](/terminal/usage/data/api-keys.md) for information on how to obtain and set a key for FRED.

:::

## Usage

Enter the Fixed Income menu by typing `fixedincome` into the Terminal from the Main menu, or use the absolute path:

```console
/fixedincome
```

![Screenshot 2023-11-03 at 10 00 27 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/f1f00a5e-e55b-48b5-9298-01886ecc3c3f)

The menu has groups of commands related to the type of data:

- Reference Rates
- Central Bank Rates
- Government Bonds
- Corporate Bonds
- Spreads

Most commands are a time series, and they will have `--start` and `--end` arguments.  The specific series can be selected in functions where a `--parameter` argument is supplied.

![Screenshot 2023-11-03 at 10 45 28 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/69a146fd-4849-499b-8c59-5f55b31ddae0)

### SOFR

Enter, `sofr`, to get the Secured Overnight Financing Rate as a chart.

```console
/fixedincome/sofr
```

![Screenshot 2023-11-03 at 10 48 07 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/5c769dd2-226e-44d5-bebf-baca2cb1b5bf)

### USRates

The `usrates` command is parameterized for:

- TIPS (tips)
- Bills (tbill)
- Constant Maturity (cmn)

The lengths of duration will differ between the three.  To see the available combinations, use the `--options` flag.

```console
/fixedincome/usrates --options
```

|         | tbill   | cmn    | tips   |
|:--------|:--------|:-------|:-------|
| 4_week  | DTB4WK  | -      | -      |
| 1_month | -       | DGS1MO | -      |
| 3_month | TB3MS   | DGS3MO | -      |
| 6_month | DTB6    | DGS6MO | -      |
| 1_year  | DTB1YR  | DGS1   | -      |
| 2_year  | -       | DGS2   | -      |
| 3_year  | -       | DGS3   | -      |
| 5_year  | -       | DGS5   | DFII5  |
| 7_year  | -       | DGS7   | DFII7  |
| 10_year | -       | DGS10  | DFII10 |
| 20_year | -       | DGS20  | DFII20 |
| 30_year | -       | DGS30  | DFII30 |

Make the selection with a syntax like:

```
/fixedincome/usrates -p tbill -m 1_year --start 2009-01-01
```

![Screenshot 2023-11-03 at 11 03 11 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/b84d4713-c7da-4fe2-a8a6-3ae15834d8fc)

### ICESpread

The `icespread` command are the Option-Adjusted Spreads from the ICE BofA Corporate Bond Index series.

Adding, `--category duration`, will place all of the US indices on the same chart.

```console
icespread --category duration
```

![Screenshot 2023-11-03 at 11 11 04 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/18c77008-4bf1-44e7-a3e6-0fbb37a5e3bd)


### Treasury

The `treasury` command allows the comparison between multiple countries at the short or long ends of rates.

```console
treasury --forecast --short united_kingdom,united_states,germany --start 2014-01-01
```

![Screenshot 2023-11-03 at 11 21 14 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/9122ae5b-4a58-4aaa-87c1-adedb5ddf4c0)

### YCRV

The `ycrv` command displays the yield curve on a specific date.  The default state is the most recent.  To view a historical date, add the `--date` argument.

```console
ycrv --date 2008-11-03
```

![Screenshot 2023-11-03 at 11 25 18 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/14f9ff75-d2ed-4e29-af94-2598c7fae95e)

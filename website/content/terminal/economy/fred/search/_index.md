```
usage: search [-s SERIES_TERM] [-n NUM] [-h]
```

Print series notes when searching for series. [Source: FRED]

```
optional arguments:
  -s SERIES_TERM, --series SERIES_TERM
                        Search for this series term. (default: None)
  -n NUM, --num NUM     Maximum number of series notes to display. (default: 5)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 16, 03:36 (✨) /economy/fred/ $ search inflation -n 10
                                                                        Search results for inflation
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Series ID      ┃ Title                                             ┃ Description                                                                                          ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ DFII10         │ Market Yield on U.S. Treasury Securities at       │ For further information regarding treasury constant maturity data, please refer to the Board of      │
│                │ 10-Year Constant Maturity, Inflation-Indexed      │ Governors ( http://www.federalreserve.gov/releases/h15/current/h15.pdf) and the Treasury             │
│                │                                                   │ (http://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/yieldmethod.aspx).   │
├────────────────┼───────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ T10YIE         │ 10-Year Breakeven Inflation Rate                  │ The breakeven inflation rate represents a measure of expected inflation derived from 10-Year         │
│                │                                                   │ Treasury Constant Maturity Securities (BC_10YEAR) and 10-Year Treasury Inflation-Indexed Constant    │
│                │                                                   │ Maturity Securities (TC_10YEAR). The latest value implies what market participants expect inflation  │
│                │                                                   │ to be in the next 10 years, on average. Starting with the update on June 21, 2019, the Treasury bond │
│                │                                                   │ data used in calculating interest rate spreads is obtained directly from the U.S. Treasury           │
│                │                                                   │ Department (https://www.treasury.gov/resource-center/data-chart-center/interest-                     │
│                │                                                   │ rates/Pages/TextView.aspx?data=yield).                                                               │
├────────────────┼───────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ FII10          │ Market Yield on U.S. Treasury Securities at       │ For further information regarding treasury constant maturity data, please refer to                   │
│                │ 10-Year Constant Maturity, Inflation-Indexed      │ http://www.federalreserve.gov/releases/h15/current/h15.pdf and http://www.treasury.gov/resource-     │
│                │                                                   │ center/data-chart-center/interest-rates/Pages/yieldmethod.aspx.                                      │
├────────────────┼───────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ WFII10         │ Market Yield on U.S. Treasury Securities at       │ For further information regarding treasury constant maturity data, please refer to                   │
│                │ 10-Year Constant Maturity, Inflation-Indexed      │ http://www.federalreserve.gov/releases/h15/current/h15.pdf and http://www.treasury.gov/resource-     │
│                │                                                   │ center/data-chart-center/interest-rates/Pages/yieldmethod.aspx.                                      │
├────────────────┼───────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ T10YIEM        │ 10-Year Breakeven Inflation Rate                  │ The breakeven inflation rate represents a measure of expected inflation derived from 10-Year         │
│                │                                                   │ Treasury Constant Maturity Securities (BC_10YEARM) and 10-Year Treasury Inflation-Indexed Constant   │
│                │                                                   │ Maturity Securities (TC_10YEARM). The latest value implies what market participants expect inflation │
│                │                                                   │ to be in the next 10 years, on average. Starting with the update on June 21, 2019, the Treasury bond │
│                │                                                   │ data used in calculating interest rate spreads is obtained directly from the U.S. Treasury           │
│                │                                                   │ Department (https://www.treasury.gov/resource-center/data-chart-center/interest-                     │
│                │                                                   │ rates/Pages/TextView.aspx?data=yield).                                                               │
├────────────────┼───────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ T5YIE          │ 5-Year Breakeven Inflation Rate                   │ The breakeven inflation rate represents a measure of expected inflation derived from 5-Year Treasury │
│                │                                                   │ Constant Maturity Securities (BC_5YEAR) and 5-Year Treasury Inflation-Indexed Constant Maturity      │
│                │                                                   │ Securities (TC_5YEAR). The latest value implies what market participants expect inflation to be in   │
│                │                                                   │ the next 5 years, on average. Starting with the update on June 21, 2019, the Treasury bond data used │
│                │                                                   │ in calculating interest rate spreads is obtained directly from the U.S. Treasury Department          │
│                │                                                   │ (https://www.treasury.gov/resource-center/data-chart-center/interest-                                │
│                │                                                   │ rates/Pages/TextView.aspx?data=yield).                                                               │
├────────────────┼───────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ T5YIFR         │ 5-Year, 5-Year Forward Inflation Expectation Rate │ This series is a measure of expected inflation (on average) over the five-year period that begins    │
│                │                                                   │ five years from today.  This series is constructed as: (((((1+((BC_10YEAR-                           │
│                │                                                   │ TC_10YEAR)/100))^10)/((1+((BC_5YEAR-TC_5YEAR)/100))^5))^0.2)-1)*100  where BC10_YEAR, TC_10YEAR,     │
│                │                                                   │ BC_5YEAR, and TC_5YEAR are the 10 year and 5 year nominal and inflation adjusted Treasury            │
│                │                                                   │ securities. All of those are the actual series IDs in FRED. Starting with the update on June 21,     │
│                │                                                   │ 2019, the Treasury bond data used in calculating interest rate spreads is obtained directly from the │
│                │                                                   │ U.S. Treasury Department (https://www.treasury.gov/resource-center/data-chart-center/interest-       │
│                │                                                   │ rates/Pages/TextView.aspx?data=yield).                                                               │
├────────────────┼───────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ FPCPITOTLZGUSA │ Inflation, consumer prices for the United States  │ Inflation as measured by the consumer price index reflects the annual percentage change in the cost  │
│                │                                                   │ to the average consumer of acquiring a basket of goods and services that may be fixed or changed at  │
│                │                                                   │ specified intervals, such as yearly. The Laspeyres formula is generally used.  International         │
│                │                                                   │ Monetary Fund, International Financial Statistics and data files.                                    │
├────────────────┼───────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ T5YIEM         │ 5-Year Breakeven Inflation Rate                   │ The breakeven inflation rate represents a measure of expected inflation derived from 5-Year Treasury │
│                │                                                   │ Constant Maturity Securities (BC_5YEAR) and 5-Year Treasury Inflation-Indexed Constant Maturity      │
│                │                                                   │ Securities (TC_5YEAR). The latest value implies what market participants expect inflation to be in   │
│                │                                                   │ the next 5 years, on average. Starting with the update on June 21, 2019, the Treasury bond data used │
│                │                                                   │ in calculating interest rate spreads is obtained directly from the U.S. Treasury Department          │
│                │                                                   │ (https://www.treasury.gov/resource-center/data-chart-center/interest-                                │
│                │                                                   │ rates/Pages/TextView.aspx?data=yield).                                                               │
├────────────────┼───────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ T5YIFRM        │ 5-Year, 5-Year Forward Inflation Expectation Rate │ This series is a measure of expected inflation (on average) over the five-year period that begins    │
│                │                                                   │ five years from today.  This series is constructed as: (((((1+((BC_10YEAR-                           │
│                │                                                   │ TC_10YEAR)/100))^10)/((1+((BC_5YEAR-TC_5YEAR)/100))^5))^0.2)-1)*100  where BC10_YEAR, TC_10YEAR,     │
│                │                                                   │ BC_5YEAR, and TC_5YEAR are the 10 year and 5 year nominal and inflation adjusted Treasury            │
│                │                                                   │ securities. All of those are the actual series IDs in FRED. Starting with the update on June 21,     │
│                │                                                   │ 2019, the Treasury bond data used in calculating interest rate spreads is obtained directly from the │
│                │                                                   │ U.S. Treasury Department (https://www.treasury.gov/resource-center/data-chart-center/interest-       │
│                │                                                   │ rates/Pages/TextView.aspx?data=yield).                                                               │
└────────────────┴───────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

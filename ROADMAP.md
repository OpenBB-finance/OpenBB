# Roadmap 📍

## Table of contents

* [Discovery](#Discovery)
* [Behavioral Analysis](#Behavioral-Analysis)
* [Sell-side Equity Research](#Sell-side-Equity-Research)
* [Fundamental Analysis](#Fundamental-Analysis)
* [Technical Analysis](#Technical-Analysis)
* [Due Diligence](#Due-Diligence)
* [Prediction Techniques](#Prediction-Techniques)
* [Reports](#Reports)
* [Comparison Analysis](#Comparison-Analysis)
* [Exploratory Data Analysis](#Exploratory-Data-Analysis)
* [Residual Analysis](#Residual-Analysis)
* [Portfolio Analysis](#Portfolio-Analysis)
* [FRED](#FRED)
* [Options](#Options)
* [Credit Analysis](#Credit-Analysis)
* [Cryptocurrencies](#Cryptocurrencies)

## Additional

* [Backend](#Backend)
* [Frontend](#Frontend)
* [Developer Experience](#Developer-Experience)
* [User Experience](#User-Experience)

---

## Discovery

### Short term

* [x] Top Losers (@didier) - [PR #171](https://github.com/DidierRLopes/GamestonkTerminal/pull/171)
* [x] ARK orders (@aia) - [PR #140](https://github.com/DidierRLopes/GamestonkTerminal/pull/140)

### Long term

* [ ] Add screeners (@didier)

---

## Behavioral Analysis

### Short term

* [ ] Implement a better Twitter client (@aia)
* [x] Add FinBrain sentiment from news (@didier) - [PR #223](https://github.com/DidierRLopes/GamestonkTerminal/pull/223)

### Long term

* [ ] Add Stocktwits (@aia)

---

## Sell-side Equity Research

### Short term

### Long term

* [ ] Add logic to Equity pull data from Bank of America, Charles Schwab

---

## Fundamental Analysis

### Short term

* [x] Rearrange FA menu to have AV and FMP as submenus (@didier) - [PR #166](https://github.com/DidierRLopes/GamestonkTerminal/pull/166)
* [ ] Add Treasury Yield Curve data (@aia) - [PR #281](https://github.com/DidierRLopes/GamestonkTerminal/pull/281)

### Long term

---

## Technical Analysis

### Short term

* [ ] Add auto-recognition of major TA patterns (@didier)
* [x] Add initial implementation of trendline analysis (@aia) - [PR #173](https://github.com/DidierRLopes/GamestonkTerminal/pull/173)
* [x] Add technical summary report provided by FinBrain (@didier) - [PR #294](https://github.com/DidierRLopes/GamestonkTerminal/pull/294)

### Long term

---

## Due Diligence

### Short term

### Long term

---

## Prediction Techniques

### Short term

* [x] Add several exponential smoothing techniques (@didier) - [PR #132](https://github.com/DidierRLopes/GamestonkTerminal/pull/132)
* [x] Allow backtesting (@didier) - [PR #169](https://github.com/DidierRLopes/GamestonkTerminal/pull/169)
* [x] Add averaging around multiple predictions (@didier) - [PR #252](https://github.com/DidierRLopes/GamestonkTerminal/pull/252)
* [ ] CNN 1D (@didier)

### Long term

* [ ] Combine Sentiment Analysis with Chart data - [IS #240](https://github.com/DidierRLopes/GamestonkTerminal/issues/240)
* [ ] Cross-Validation methods (Forward Chaining, K-Fold, Group K-Fold) (@didier)

---

## Reports

### Short term

* [ ] Expand Due Diligence report (@aia)
* [ ] Add multi-ticker comparison report (@aia)
* [x] Add Economy analysis report (@aia) - [PR #205](https://github.com/DidierRLopes/GamestonkTerminal/pull/205)
* [ ] Add interest rate analysis to Economy report (@aia)
* [ ] Add a report for major business categories - growth vs value, cyclicals, small-cap vs large-caps (@aia)

### Long term

---

## Comparison Analysis

### Short term

* [x] Add multi-ticker historical data comparison (@didier) - [PR #141](https://github.com/DidierRLopes/GamestonkTerminal/pull/141)
* [x] Add multi-ticker financials comparison (@didier) - [PR #237](https://github.com/DidierRLopes/GamestonkTerminal/pull/237)
* [x] Add multi-ticker sentiment comparison (@didier) - [PR #250](https://github.com/DidierRLopes/GamestonkTerminal/pull/250)

### Long term

---

## Exploratory Data Analysis

### Short term

* [x] Summary statistics, cdf, histogram, box-whiskers, cusum, decompose (@didier) - [PR #289](https://github.com/DidierRLopes/GamestonkTerminal/pull/289)

### Long term

---

## Residual Analysis

### Short term

* [x] Residuals analysis menu with histogram, qqplot, acf, hypothesis tests (e.g. Kurtosis, Jarques-Bera, ARCH, ADF) (@didier) - [PR #292](https://github.com/DidierRLopes/GamestonkTerminal/pull/292)

### Long term

---

## Portfolio Analysis

### Short term

* [x] Add alpaca (@jmaslek) - [PR #259](https://github.com/DidierRLopes/GamestonkTerminal/pull/229)
* [x] Add robinhood (@jmaslek) - [PR #229](https://github.com/DidierRLopes/GamestonkTerminal/pull/229)
* [x] Add Ally Invest (@jmaslek)
* [x] Merge data from different brokers (@jmaslek)
* [x] Add more options around merged portfolios
* [ ] Add Brokers (td, webull, etc) (@jmaslek)
* [ ] Refactoring

### Long term

* [ ] Summaries / tear sheets (@jmaslek)
* [ ] Portfolio Optimization (@jmaslek)


---

## FRED

### Short term

* [x] Implement Economic data (gpd, unemployment rate, ...) (@jmaslek) - [PR #167](https://github.com/DidierRLopes/GamestonkTerminal/pull/167)

### Long term

---

## Options

### Short term

* [x] Add Volume graph (@lolrenx) - [PR #209](https://github.com/DidierRLopes/GamestonkTerminal/pull/209)
* [x] Add Open Interest graph (@lolrenx) - [PR #209](https://github.com/DidierRLopes/GamestonkTerminal/pull/209)

### Long term

* [ ] Add max pain graph (@lolrenx)

---

## Credit Analysis

### Short term

### Long term

* [ ] Add FINRA
* [ ] Moodies data

---

## Cryptocurrencies

### Short term

* [x] Add Coingecko (@jmaslek) - [PR #283](#https://github.com/DidierRLopes/GamestonkTerminal/pulls)
* [ ] Add [Coinpaprika](https://coinpaprika.com/api/)
* [ ] Add crypto charts

### Long term

---

## Backend

### Short term

* [ ] Logging (@aia)
* [ ] Secure storage of credentials (@aia)

### Long term

* [ ] Add caching
* [ ] APIs
* [ ] GraphQL

---

## Frontend

### Short term

* [x] Add terminal flair (@aia) - [PR #131](https://github.com/DidierRLopes/GamestonkTerminal/pull/131)
* [x] Prompt-toolkit (@ricleal) - [PR #142](https://github.com/DidierRLopes/GamestonkTerminal/pull/142)
* [x] Add thought of the day (@aia) - [PR #233](https://github.com/DidierRLopes/GamestonkTerminal/pull/233)

### Long term

---

## Developer Experience

### Short term

* [x] Add Windows CI (@aia) - [PR #151](https://github.com/DidierRLopes/GamestonkTerminal/pull/151)
* [ ] Write a developer guide
* [ ] Add a docker CI
* [x] Add Feature Flags (@aia) - [PR #158](https://github.com/DidierRLopes/GamestonkTerminal/pull/158)
* [x] Add ad-hoc builds (@aia) - [PR #192](https://github.com/DidierRLopes/GamestonkTerminal/pull/192)
* [x] Add test generators and test parametrization helpers (@aia) - [PR #264](https://github.com/DidierRLopes/GamestonkTerminal/pull/264)
* [ ] Reorganize tests to separate Unit and Integration
* [ ] Versioning

### Long term

---

## User Experience

### Short term

* [ ] Publish Docker
* [ ] Most commands to have export flag to save output into csv/txt file
* [ ] Most commands to have save flag to save image into png/jpg file

### Long term

* [ ] Add a WHL installation

---

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
* [Portfolio Optimization](#Portfolio-Optimization)
* [Economy](#Economy)
* [Options](#Options)
* [Credit Analysis](#Credit-Analysis)
* [Cryptocurrencies](#Cryptocurrencies)
* [Screener](#Screener)
* [Forex](#Forex)
* [Backtesting](#Backtesting)
* [Resource Collection](#Resource-Collection)

## Additional

* [Backend](#Backend)
* [Frontend](#Frontend)
* [Developer Experience](#Developer-Experience)
* [User Experience](#User-Experience)

---

## Discovery
* [x] Top Losers (@didier) - [PR #171](https://github.com/DidierRLopes/GamestonkTerminal/pull/171)
* [x] ARK orders (@aia) - [PR #140](https://github.com/DidierRLopes/GamestonkTerminal/pull/140)
* [x] Analyse sectors/industry performance, overview and valuation from Finviz (@didier) - [PR #315](https://github.com/DidierRLopes/GamestonkTerminal/pull/315)
* [x] Add latest and trending news commands (@hinxx) - [PR #347](https://github.com/DidierRLopes/GamestonkTerminal/pull/347)
* [x] Add top ratings updates (@hinxx) - [PR #357](https://github.com/DidierRLopes/GamestonkTerminal/pull/357)
* [x] Add dark pool (ATS) data of tickers with growing trades activity (@didier) - [PR #372](https://github.com/DidierRLopes/GamestonkTerminal/pull/372)


**NEXT**


---

## Behavioral Analysis
* [x] Add FinBrain sentiment from news (@didier) - [PR #223](https://github.com/DidierRLopes/GamestonkTerminal/pull/223)

**NEXT**
* [ ] Implement a better Twitter client (@aia)
* [ ] Add Stocktwits (@aia)

---

## Sell-side Equity Research
* [x] Add stockanalysis to research menu - [PR #185](https://github.com/DidierRLopes/GamestonkTerminal/pull/185)

**NEXT**
* [ ] Add logic to Equity pull data from Bank of America, Charles Schwab

---

## Fundamental Analysis
* [x] Rearrange FA menu to have AV and FMP as submenus (@didier) - [PR #166](https://github.com/DidierRLopes/GamestonkTerminal/pull/166)
* [x] Add Fundamental Analysis score (@didier) - [PR #383](https://github.com/DidierRLopes/GamestonkTerminal/pull/383)

**NEXT**
* [ ] Add Treasury Yield Curve data (@aia) - [PR #281](https://github.com/DidierRLopes/GamestonkTerminal/pull/281)

---

## Technical Analysis
* [x] Add initial implementation of trendline analysis (@aia) - [PR #173](https://github.com/DidierRLopes/GamestonkTerminal/pull/173)
* [x] Add technical summary report provided by FinBrain (@didier) - [PR #294](https://github.com/DidierRLopes/GamestonkTerminal/pull/294)
* [x] Add recommendation based on technical indicators from Tradingview (@didier) - [PR #301](https://github.com/DidierRLopes/GamestonkTerminal/pull/301)
* [x] Add view of stock historical price with trendlines (support, resistance) by Finviz (@didier) - [PR #317](https://github.com/DidierRLopes/GamestonkTerminal/pull/317)

**NEXT**
* [ ] Add auto-recognition of major TA patterns (@didier)

---

## Due Diligence
* [x] Add dark pools (ATS) vs Non-ATS data over time (@didier) - [PR #363](https://github.com/DidierRLopes/GamestonkTerminal/pull/363)
* [x] Add failure to deliver command (@hinxx) - [PR #366](#https://github.com/DidierRLopes/GamestonkTerminal/pull/366)

**NEXT**

---

## Prediction Techniques
* [x] Add several exponential smoothing techniques (@didier) - [PR #132](https://github.com/DidierRLopes/GamestonkTerminal/pull/132)
* [x] Allow backtesting (@didier) - [PR #169](https://github.com/DidierRLopes/GamestonkTerminal/pull/169)
* [x] Add averaging around multiple predictions (@didier) - [PR #252](https://github.com/DidierRLopes/GamestonkTerminal/pull/252)

**NEXT**
* [ ] CNN 1D (@didier)
* [ ] Combine Sentiment Analysis with Chart data - [IS #240](https://github.com/DidierRLopes/GamestonkTerminal/issues/240)
* [ ] Cross-Validation methods (Forward Chaining, K-Fold, Group K-Fold) (@didier)

---

## Reports
* [x] Add Economy analysis report (@aia) - [PR #205](https://github.com/DidierRLopes/GamestonkTerminal/pull/205)

**NEXT**
* [ ] Expand Due Diligence report (@aia)
* [ ] Add multi-ticker comparison report (@aia)
* [ ] Add interest rate analysis to Economy report (@aia)
* [ ] Add a report for major business categories - growth vs value, cyclicals, small-cap vs large-caps (@aia)

---

## Comparison Analysis
* [x] Add multi-ticker historical data comparison (@didier) - [PR #141](https://github.com/DidierRLopes/GamestonkTerminal/pull/141)
* [x] Add multi-ticker financials comparison (@didier) - [PR #237](https://github.com/DidierRLopes/GamestonkTerminal/pull/237)
* [x] Add multi-ticker sentiment comparison (@didier) - [PR #250](https://github.com/DidierRLopes/GamestonkTerminal/pull/250)
* [x] Get similar companies from Finviz based on Industry and Sector (and possibly country) from Finviz (@didier) - [PR #323](https://github.com/DidierRLopes/GamestonkTerminal/pull/323)
* [x] Output brief screen  (overview, performance, financial, valuation) across similar companies (@didier) - [PR #323](https://github.com/DidierRLopes/GamestonkTerminal/pull/323)
* [x] Add command to take tickers to portfolio optimization (@jmaslek) - [PR #329](https://github.com/DidierRLopes/GamestonkTerminal/pull/329)

**NEXT**



---

## Exploratory Data Analysis
* [x] Summary statistics, cdf, histogram, box-whiskers, cusum, decompose (@didier) - [PR #289](https://github.com/DidierRLopes/GamestonkTerminal/pull/289)

**NEXT**

---

## Residual Analysis
* [x] Residuals analysis menu with histogram, qqplot, acf, hypothesis tests (e.g. Kurtosis, Jarques-Bera, ARCH, ADF) (@didier) - [PR #292](https://github.com/DidierRLopes/GamestonkTerminal/pull/292)

**NEXT**

---

## Portfolio Analysis
* [x] Add alpaca (@jmaslek) - [PR #259](https://github.com/DidierRLopes/GamestonkTerminal/pull/229)
* [x] Add robinhood (@jmaslek) - [PR #229](https://github.com/DidierRLopes/GamestonkTerminal/pull/229)
* [x] Add Ally Invest (@jmaslek) - [PR #267](https://github.com/DidierRLopes/GamestonkTerminal/pull/267)
* [x] Degiro support (@deel) - [PR #381](https://github.com/DidierRLopes/GamestonkTerminal/pull/381)

**NEXT**
* [ ] Merge data from different brokers (@jmaslek)
* [ ] Add more options around merged portfolios
* [ ] Add Brokers (td, webull, etc) (@jmaslek)
* [ ] Refactoring
* [ ] Summaries / tear sheets (@jmaslek)

___

## Portfolio Optimization
* [x] Basic Optimization through PyPortFolioOpt(@jmaslek) - [PR #329](https://github.com/DidierRLopes/GamestonkTerminal/pull/329)
* [x] Add command to maximise the quadratic utility(@didier) - [PR #349](https://github.com/DidierRLopes/GamestonkTerminal/pull/349)

**NEXT**
* [ ] Allow for more custom optimization constrains


---

## Economy
* [x] Implement Economic data (gpd, unemployment rate, ...) (@jmaslek) - [PR #167](https://github.com/DidierRLopes/GamestonkTerminal/pull/167)
* [x] Refactor FRED to ECON menu and add VIX view (@jmaslek) - [PR #405](https://github.com/DidierRLopes/GamestonkTerminal/pull/405)

**NEXT**

---

## Options
* [x] Add Volume graph (@lolrenx) - [PR #209](https://github.com/DidierRLopes/GamestonkTerminal/pull/209)
* [x] Add Open Interest graph (@lolrenx) - [PR #209](https://github.com/DidierRLopes/GamestonkTerminal/pull/209)
* [x] Add options information data (IV rank, etc) (@jmaslek) - [PR #375](https://github.com/DidierRLopes/GamestonkTerminal/pull/375)

**NEXT**
* [ ] Add max pain graph (@lolrenx)

---

## Credit Analysis

**NEXT**
* [ ] Add FINRA
* [ ] Moodies data

---

## Cryptocurrencies
* [x] Add Coingecko (@jmaslek) - [PR #283](#https://github.com/DidierRLopes/GamestonkTerminal/pull/283)
* [x] view top coins from coinmarketcap (@jmaslek) - [PR #378](https://github.com/DidierRLopes/GamestonkTerminal/pull/378)

**NEXT**
* [ ] Add [Coinpaprika](https://coinpaprika.com/api/)
* [ ] Add crypto charts
* [x] Add binance (@jmaslek)
* [ ] Add top altcoin lists
---

## Screener
* [x] Add Screener menu with overview, valuation, financial, ownership, performance, technical commands based on filter presets from Finviz (@didier) - [PR #314](https://github.com/DidierRLopes/GamestonkTerminal/pull/314)
* [x] Add README with explanation of how presets are stored and can be added by experienced users. (@didier) - [PR #314](https://github.com/DidierRLopes/GamestonkTerminal/pull/314)
* [x] Add screener signals (e.g. top gainers, new highs, most volatile, oversold, major news, ...) from Finviz (@didier) - [PR #314](https://github.com/DidierRLopes/GamestonkTerminal/pull/314)
* [x] Plot screener historical using Yahoo Finance data (@didier) - [PR #319](https://github.com/DidierRLopes/GamestonkTerminal/pull/319)
* [x] Add command to take tickers to portfolio optimization (@didier) - [PR #349](https://github.com/DidierRLopes/GamestonkTerminal/pull/349)
* [x] Add flags to save screeners and run papermill on returned tickers (@alokan) - [PR #414](https://github.com/DidierRLopes/GamestonkTerminal/pull/414)

**NEXT**

---

## Forex
* [x] Add entire forex menu through Oanda (@alokan) - [PR #360](https://github.com/DidierRLopes/GamestonkTerminal/pull/360)
* [x] Add EDA menu, Behavioural Analysis menu, Due Diligence from other users in Reddit, and latest news regarding currency provided. (@alokan) - [PR #387](https://github.com/DidierRLopes/GamestonkTerminal/pull/387)

**NEXT**


---

## Resource Collection
* [x] Add hfletters and learn commands to resource collection (@didier) - [PR #427](https://github.com/DidierRLopes/GamestonkTerminal/pull/427)


**NEXT**

---

## Backtesting
* [x] Add simple backtest menu with simple strategies and benchmarks (@jmaslek) [PR #415](https://github.com/DidierRLopes/GamestonkTerminal/pull/415)

**NEXT**

---

## Backend

**NEXT**
* [ ] Logging (@aia)
* [ ] Secure storage of credentials (@aia)
* [ ] Add caching
* [ ] APIs
* [ ] GraphQL

---

## Frontend
* [x] Add terminal flair (@aia) - [PR #131](https://github.com/DidierRLopes/GamestonkTerminal/pull/131)
* [x] Prompt-toolkit (@ricleal) - [PR #142](https://github.com/DidierRLopes/GamestonkTerminal/pull/142)
* [x] Add thought of the day (@aia) - [PR #233](https://github.com/DidierRLopes/GamestonkTerminal/pull/233)

**NEXT**

---

## Developer Experience
* [x] Add Windows CI (@aia) - [PR #151](https://github.com/DidierRLopes/GamestonkTerminal/pull/151)
* [x] Add Feature Flags (@aia) - [PR #158](https://github.com/DidierRLopes/GamestonkTerminal/pull/158)
* [x] Add ad-hoc builds (@aia) - [PR #192](https://github.com/DidierRLopes/GamestonkTerminal/pull/192)
* [x] Add test generators and test parametrization helpers (@aia) - [PR #264](https://github.com/DidierRLopes/GamestonkTerminal/pull/264)
* [x] Sphinx documentation https://gamestonk-terminal.readthedocs.io/en/latest/index.html (@piiq) - [PR #413](https://github.com/DidierRLopes/GamestonkTerminal/pull/413)

**NEXT**
* [ ] Write a developer guide
* [ ] Add a docker CI
* [ ] Reorganize tests to separate Unit and Integration
* [ ] Versioning

---

## User Experience

**NEXT**
* [ ] Publish Docker
* [ ] Most commands to have export flag to save output into csv/txt file
* [ ] Most commands to have save flag to save image into png/jpg file
* [ ] Add a WHL installation

---

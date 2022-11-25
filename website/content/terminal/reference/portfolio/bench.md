---
title: bench
description: OpenBB Terminal Function
---

# bench

Load in a benchmark from a selected list or set your own based on the ticker.

### Usage

```python
bench -b BENCHMARK [BENCHMARK ...] [-s]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| benchmark | Set the benchmark for the portfolio. By default, this is SPDR S&P 500 ETF Trust (SPY). | SPY | False | SPDR S&P 500 ETF Trust (SPY), iShares Core S&P 500 ETF (IVV), Vanguard Total Stock Market ETF (VTI), Vanguard S&P 500 ETF (VOO), Invesco QQQ Trust (QQQ), Vanguard Value ETF (VTV), Vanguard FTSE Developed Markets ETF (VEA), iShares Core MSCI EAFE ETF (IEFA), iShares Core U.S. Aggregate Bond ETF (AGG), Vanguard Total Bond Market ETF (BND), Vanguard FTSE Emerging Markets ETF (VWO), Vanguard Growth ETF (VUG), iShares Core MSCI Emerging Markets ETF (IEMG), iShares Core S&P Small-Cap ETF (IJR), SPDR Gold Shares (GLD), iShares Russell 1000 Growth ETF (IWF), iShares Core S&P Mid-Cap ETF (IJH), Vanguard Dividend Appreciation ETF (VIG), iShares Russell 2000 ETF (IWM), iShares Russell 1000 Value ETF (IWD), Vanguard Mid-Cap ETF (VO), iShares MSCI EAFE ETF (EFA), Vanguard Total International Stock ETF (VXUS), Vanguard Information Technology ETF (VGT), Vanguard High Dividend Yield Index ETF (VYM), Vanguard Total International Bond ETF (BNDX), Vanguard Real Estate ETF (VNQ), Vanguard Small Cap ETF (VB), Technology Select Sector SPDR Fund (XLK), iShares Core S&P Total U.S. Stock Market ETF (ITOT), Vanguard Intermediate-Term Corporate Bond ETF (VCIT), Vanguard Short-Term Corporate Bond ETF (VCSH), Energy Select Sector SPDR Fund (XLE), Health Care Select Sector SPDR Fund (XLV), Vanguard Short-Term Bond ETF (BSV), Financial Select Sector SPDR Fund (XLF), Schwab US Dividend Equity ETF (SCHD), Invesco S&P 500® Equal Weight ETF (RSP), iShares iBoxx $ Investment Grade Corporate Bond ETF (LQD), iShares S&P 500 Growth ETF (IVW), Vanguard FTSE All-World ex-US Index Fund (VEU), iShares TIPS Bond ETF (TIP), iShares Gold Trust (IAU), Schwab U.S. Large-Cap ETF (SCHX), iShares Core MSCI Total International Stock ETF (IXUS), iShares Russell Midcap ETF (IWR), iShares Russell 1000 ETF (IWB), SPDR Dow Jones Industrial Average ETF Trust (DIA), iShares MSCI Emerging Markets ETF (EEM), iShares MSCI USA Min Vol Factor ETF (USMV), Schwab International Equity ETF (SCHF), iShares S&P 500 Value ETF (IVE), iShares National Muni Bond ETF (MUB), Vanguard Large Cap ETF (VV), Vanguard Small Cap Value ETF (VBR), iShares ESG Aware MSCI USA ETF (ESGU), Vanguard Total World Stock ETF (VT), iShares Core Dividend Growth ETF (DGRO), iShares 1-3 Year Treasury Bond ETF (SHY), iShares Select Dividend ETF (DVY), iShares MSCI USA Quality Factor ETF (QUAL), Schwab U.S. Broad Market ETF (SCHB), iShares MBS ETF (MBB), SPDR S&P Dividend ETF (SDY), iShares 1-5 Year Investment Grade Corporate Bond ETF (IGSB), Vanguard Short-Term Inflation-Protected Securities ETF (VTIP), JPMorgan Ultra-Short Income ETF (JPST), iShares 20+ Year Treasury Bond ETF (TLT), iShares MSCI ACWI ETF (ACWI), SPDR S&P Midcap 400 ETF Trust (MDY), iShares Core Total USD Bond Market ETF (IUSB), iShares Short Treasury Bond ETF (SHV), Vanguard FTSE Europe ETF (VGK), Consumer Discretionary Select Sector SPDR Fund (XLY), SPDR Bloomberg 1-3 Month T-Bill ETF (BIL), iShares U.S. Treasury Bond ETF (GOVT), Vanguard Health Care ETF (VHT), Vanguard Mid-Cap Value ETF (VOE), Consumer Staples Select Sector SPDR Fund (XLP), Schwab U.S. TIPS ETF (SCHP), iShares 7-10 Year Treasury Bond ETF (IEF), iShares Preferred & Income Securities ETF (PFF), Utilities Select Sector SPDR Fund (XLU), Vanguard Tax-Exempt Bond ETF (VTEB), iShares MSCI EAFE Value ETF (EFV), Schwab U.S. Large-Cap Growth ETF (SCHG), iShares J.P. Morgan USD Emerging Markets Bond ETF (EMB), Dimensional U.S. Core Equity 2 ETF (DFAC), Schwab U.S. Small-Cap ETF (SCHA), VanEck Gold Miners ETF (GDX), Vanguard Mortgage-Backed Securities ETF (VMBS), ProShares UltraPro QQQ (TQQQ), Vanguard Short-Term Treasury ETF (VGSH), iShares iBoxx $ High Yield Corporate Bond ETF (HYG), Industrial Select Sector SPDR Fund (XLI), iShares Russell Mid-Cap Value ETF (IWS), Vanguard Extended Market ETF (VXF), SPDR Portfolio S&P 500 ETF (SPLG), SPDR Portfolio S&P 500 Value ETF (SPYV), iShares Russell 2000 Value ETF (IWN) |
| full_shares | Whether to only make a trade with the benchmark when a full share can be bought (no partial shares). | False | True | None |


---

## Examples

```python
2022 May 10, 09:53 (🦋) /portfolio/ $ bench Vanguard FTSE Developed Markets ETF (VEA)

Benchmark: Vanguard Developed Markets Index Fund (VEA)

2022 May 10, 09:53 (🦋) /portfolio/ $
```
---

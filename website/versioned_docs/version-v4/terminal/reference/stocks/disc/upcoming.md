---
title: upcoming
description: OpenBB Terminal Function
---

# upcoming

Upcoming earnings release dates. [Source: Seeking Alpha]

### Usage

```python
upcoming [-l LIMIT] [-p N_PAGES]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of upcoming earnings release dates to display. | 1 | True | None |
| n_pages | Number of pages to read upcoming earnings from in Seeking Alpha website. | 10 | True | None |


---

## Examples

```python
2022 Feb 16, 04:17 (🦋) /stocks/disc/ $ upcoming

            Upcoming Earnings Releases
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃       ┃ Earnings on 2022-02-16                  ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ GLDD  │ Great Lakes Dredge & Dock Corporation   │
├───────┼─────────────────────────────────────────┤
│ BCOR  │ Blucora, Inc.                           │
├───────┼─────────────────────────────────────────┤
│ BGCP  │ BGC Partners, Inc.                      │
├───────┼─────────────────────────────────────────┤
│ ADI   │ Analog Devices, Inc.                    │
├───────┼─────────────────────────────────────────┤
│ KHC   │ The Kraft Heinz Company                 │
├───────┼─────────────────────────────────────────┤
│ AMCX  │ AMC Networks Inc.                       │
├───────┼─────────────────────────────────────────┤
│ AIMC  │ Altra Industrial Motion Corp.           │
├───────┼─────────────────────────────────────────┤
│ WIX   │ Wix.com Ltd.                            │
├───────┼─────────────────────────────────────────┤
│ TTD   │ The Trade Desk, Inc.                    │
├───────┼─────────────────────────────────────────┤
│ CCEP  │ Coca-Cola Europacific Partners PLC      │
├───────┼─────────────────────────────────────────┤
│ WING  │ Wingstop Inc.                           │
├───────┼─────────────────────────────────────────┤
│ DRVN  │ Driven Brands Holdings Inc.             │
├───────┼─────────────────────────────────────────┤
│ CSCO  │ Cisco Systems, Inc.                     │
├───────┼─────────────────────────────────────────┤
│ CPRT  │ Copart, Inc.                            │
├───────┼─────────────────────────────────────────┤
│ HST   │ Host Hotels & Resorts, Inc.             │
├───────┼─────────────────────────────────────────┤
│ NVDA  │ NVIDIA Corporation                      │
├───────┼─────────────────────────────────────────┤
│ RBBN  │ Ribbon Communications Inc.              │
├───────┼─────────────────────────────────────────┤
│ TRIP  │ TripAdvisor, Inc.                       │
├───────┼─────────────────────────────────────────┤
│ RGLD  │ Royal Gold, Inc.                        │
├───────┼─────────────────────────────────────────┤
│ CRMT  │ America's Car-Mart, Inc.                │
├───────┼─────────────────────────────────────────┤
│ CAKE  │ The Cheesecake Factory Incorporated     │
├───────┼─────────────────────────────────────────┤
│ VECO  │ Veeco Instruments Inc.                  │
├───────┼─────────────────────────────────────────┤
│ SCKT  │ Socket Mobile, Inc.                     │
├───────┼─────────────────────────────────────────┤
│ PEGA  │ Pegasystems Inc.                        │
├───────┼─────────────────────────────────────────┤
│ FARO  │ FARO Technologies, Inc.                 │
├───────┼─────────────────────────────────────────┤
│ RUSHA │ Rush Enterprises, Inc.                  │
├───────┼─────────────────────────────────────────┤
│ AXTI  │ AXT, Inc.                               │
├───────┼─────────────────────────────────────────┤
│ INFN  │ Infinera Corporation                    │
├───────┼─────────────────────────────────────────┤
│ MMLP  │ Martin Midstream Partners L.P.          │
├───────┼─────────────────────────────────────────┤
│ BCOV  │ Brightcove Inc.                         │
├───────┼─────────────────────────────────────────┤
│ ROIC  │ Retail Opportunity Investments Corp.    │
├───────┼─────────────────────────────────────────┤
│ TRUP  │ Trupanion, Inc.                         │
├───────┼─────────────────────────────────────────┤
│ LOPE  │ Grand Canyon Education, Inc.            │
├───────┼─────────────────────────────────────────┤
│ OPI   │ Office Properties Income Trust          │
├───────┼─────────────────────────────────────────┤
│ EVER  │ EverQuote, Inc.                         │
├───────┼─────────────────────────────────────────┤
│ CONE  │ CyrusOne Inc.                           │
├───────┼─────────────────────────────────────────┤
│ MTTR  │ Matterport, Inc.                        │
├───────┼─────────────────────────────────────────┤
│ TXG   │ 10x Genomics, Inc.                      │
├───────┼─────────────────────────────────────────┤
│ APP   │ AppLovin Corporation                    │
├───────┼─────────────────────────────────────────┤
│ AMPL  │ Amplitude, Inc.                         │
├───────┼─────────────────────────────────────────┤
│ CTRE  │ CareTrust REIT, Inc.                    │
├───────┼─────────────────────────────────────────┤
│ KNBE  │ KnowBe4, Inc.                           │
├───────┼─────────────────────────────────────────┤
│ SBLK  │ Star Bulk Carriers Corp.                │
├───────┼─────────────────────────────────────────┤
│ OCDX  │ Ortho Clinical Diagnostics Holdings plc │
├───────┼─────────────────────────────────────────┤
│ OM    │ Outset Medical, Inc.                    │
├───────┼─────────────────────────────────────────┤
│ ACVA  │ ACV Auctions Inc.                       │
├───────┼─────────────────────────────────────────┤
│ CNDT  │ Conduent Incorporated                   │
├───────┼─────────────────────────────────────────┤
│ AUR   │ Aurora Innovation, Inc.                 │
├───────┼─────────────────────────────────────────┤
│ IBEX  │ IBEX Limited                            │
├───────┼─────────────────────────────────────────┤
│ GRIN  │ Grindrod Shipping Holdings Ltd.         │
├───────┼─────────────────────────────────────────┤
│ PLMR  │ Palomar Holdings, Inc.                  │
├───────┼─────────────────────────────────────────┤
│ GLBE  │ Global-e Online Ltd.                    │
├───────┼─────────────────────────────────────────┤
│ WKME  │ WalkMe Ltd.                             │
├───────┼─────────────────────────────────────────┤
│ ALKS  │ Alkermes plc                            │
├───────┼─────────────────────────────────────────┤
│ QUIK  │ QuickLogic Corporation                  │
├───────┼─────────────────────────────────────────┤
│ SPWR  │ SunPower Corporation                    │
├───────┼─────────────────────────────────────────┤
│ BPMC  │ Blueprint Medicines Corporation         │
├───────┼─────────────────────────────────────────┤
│ GOGL  │ Golden Ocean Group Limited              │
├───────┼─────────────────────────────────────────┤
│ GLDD  │ Great Lakes Dredge & Dock Corporation   │
├───────┼─────────────────────────────────────────┤
│ BCOR  │ Blucora, Inc.                           │
├───────┼─────────────────────────────────────────┤
│ BGCP  │ BGC Partners, Inc.                      │
├───────┼─────────────────────────────────────────┤
│ ADI   │ Analog Devices, Inc.                    │
├───────┼─────────────────────────────────────────┤
│ KHC   │ The Kraft Heinz Company                 │
├───────┼─────────────────────────────────────────┤
│ AMCX  │ AMC Networks Inc.                       │
├───────┼─────────────────────────────────────────┤
│ AIMC  │ Altra Industrial Motion Corp.           │
├───────┼─────────────────────────────────────────┤
│ WIX   │ Wix.com Ltd.                            │
├───────┼─────────────────────────────────────────┤
│ TTD   │ The Trade Desk, Inc.                    │
├───────┼─────────────────────────────────────────┤
│ CCEP  │ Coca-Cola Europacific Partners PLC      │
├───────┼─────────────────────────────────────────┤
│ WING  │ Wingstop Inc.                           │
├───────┼─────────────────────────────────────────┤
│ DRVN  │ Driven Brands Holdings Inc.             │
├───────┼─────────────────────────────────────────┤
│ CSCO  │ Cisco Systems, Inc.                     │
├───────┼─────────────────────────────────────────┤
│ CPRT  │ Copart, Inc.                            │
├───────┼─────────────────────────────────────────┤
│ HST   │ Host Hotels & Resorts, Inc.             │
├───────┼─────────────────────────────────────────┤
│ NVDA  │ NVIDIA Corporation                      │
├───────┼─────────────────────────────────────────┤
│ RBBN  │ Ribbon Communications Inc.              │
├───────┼─────────────────────────────────────────┤
│ TRIP  │ TripAdvisor, Inc.                       │
├───────┼─────────────────────────────────────────┤
│ RGLD  │ Royal Gold, Inc.                        │
├───────┼─────────────────────────────────────────┤
│ CRMT  │ America's Car-Mart, Inc.                │
├───────┼─────────────────────────────────────────┤
│ CAKE  │ The Cheesecake Factory Incorporated     │
├───────┼─────────────────────────────────────────┤
│ VECO  │ Veeco Instruments Inc.                  │
├───────┼─────────────────────────────────────────┤
│ SCKT  │ Socket Mobile, Inc.                     │
├───────┼─────────────────────────────────────────┤
│ PEGA  │ Pegasystems Inc.                        │
├───────┼─────────────────────────────────────────┤
│ FARO  │ FARO Technologies, Inc.                 │
├───────┼─────────────────────────────────────────┤
│ RUSHA │ Rush Enterprises, Inc.                  │
├───────┼─────────────────────────────────────────┤
│ AXTI  │ AXT, Inc.                               │
├───────┼─────────────────────────────────────────┤
│ INFN  │ Infinera Corporation                    │
├───────┼─────────────────────────────────────────┤
│ MMLP  │ Martin Midstream Partners L.P.          │
├───────┼─────────────────────────────────────────┤
│ BCOV  │ Brightcove Inc.                         │
├───────┼─────────────────────────────────────────┤
│ ROIC  │ Retail Opportunity Investments Corp.    │
├───────┼─────────────────────────────────────────┤
│ TRUP  │ Trupanion, Inc.                         │
├───────┼─────────────────────────────────────────┤
│ LOPE  │ Grand Canyon Education, Inc.            │
├───────┼─────────────────────────────────────────┤
│ OPI   │ Office Properties Income Trust          │
├───────┼─────────────────────────────────────────┤
│ EVER  │ EverQuote, Inc.                         │
├───────┼─────────────────────────────────────────┤
│ CONE  │ CyrusOne Inc.                           │
├───────┼─────────────────────────────────────────┤
│ MTTR  │ Matterport, Inc.                        │
├───────┼─────────────────────────────────────────┤
│ TXG   │ 10x Genomics, Inc.                      │
├───────┼─────────────────────────────────────────┤
│ APP   │ AppLovin Corporation                    │
├───────┼─────────────────────────────────────────┤
│ AMPL  │ Amplitude, Inc.                         │
├───────┼─────────────────────────────────────────┤
│ CTRE  │ CareTrust REIT, Inc.                    │
├───────┼─────────────────────────────────────────┤
│ KNBE  │ KnowBe4, Inc.                           │
├───────┼─────────────────────────────────────────┤
│ SBLK  │ Star Bulk Carriers Corp.                │
├───────┼─────────────────────────────────────────┤
│ OCDX  │ Ortho Clinical Diagnostics Holdings plc │
├───────┼─────────────────────────────────────────┤
│ OM    │ Outset Medical, Inc.                    │
├───────┼─────────────────────────────────────────┤
│ ACVA  │ ACV Auctions Inc.                       │
├───────┼─────────────────────────────────────────┤
│ CNDT  │ Conduent Incorporated                   │
├───────┼─────────────────────────────────────────┤
│ AUR   │ Aurora Innovation, Inc.                 │
├───────┼─────────────────────────────────────────┤
│ IBEX  │ IBEX Limited                            │
├───────┼─────────────────────────────────────────┤
│ GRIN  │ Grindrod Shipping Holdings Ltd.         │
├───────┼─────────────────────────────────────────┤
│ PLMR  │ Palomar Holdings, Inc.                  │
├───────┼─────────────────────────────────────────┤
│ GLBE  │ Global-e Online Ltd.                    │
├───────┼─────────────────────────────────────────┤
│ WKME  │ WalkMe Ltd.                             │
├───────┼─────────────────────────────────────────┤
│ ALKS  │ Alkermes plc                            │
├───────┼─────────────────────────────────────────┤
│ QUIK  │ QuickLogic Corporation                  │
├───────┼─────────────────────────────────────────┤
│ SPWR  │ SunPower Corporation                    │
├───────┼─────────────────────────────────────────┤
│ BPMC  │ Blueprint Medicines Corporation         │
├───────┼─────────────────────────────────────────┤
│ GOGL  │ Golden Ocean Group Limited              │
└───────┴─────────────────────────────────────────┘
```
---

---
title: cr
description: OpenBB Terminal Function
---

# cr

Displays crypto {borrow,supply} interest rates for cryptocurrencies across several platforms. You can select rate type with --type {borrow,supply} You can display only N number of platforms with --limit parameter.

### Usage

```python
cr [-t {borrow,supply}] [-c CRYPTOS] [-p PLATFORMS]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| type | Select interest rate type | supply | True | borrow, supply |
| cryptos | Cryptocurrencies to search interest rates for separated by comma. Default: BTC,ETH,USDT,USDC. Options: ZRX,BAT,REP,ETH,SAI,BTC,XRP,LTC,EOS,BCH,XMR,DOGE,USDC,USDT,BSV,NEO,ETC,OMG,ZEC,BTG,SAN,DAI,UNI,WBTC,COMP,LUNA,UST,BUSD,KNC,LEND,LINK,MANA,MKR,SNX,SUSD,TUSD,eCRV-DAO,HEGIC,YFI,1INCH,CRV-IB,CRV-HBTC,BOOST,CRV-sBTC,CRV-renBTC,CRV-sAave,CRV-oBTC,CRV-pBTC,CRV-LUSD,CRV-BBTC,CRV-tBTC,CRV-FRAX,CRV-yBUSD,CRV-COMP,CRV-GUSD,yUSD,CRV-3pool,CRV-TUSD,CRV-BUSD,CRV-DUSD,CRV-UST,CRV-mUSD,sUSD,CRV-sUSD,CRV-LINK,CRV-USDN,CRV-USDP,CRV-alUSD,CRV-Aave,CRV-HUSD,CRV-EURS,RAI,CRV-triCrypto,CRV-Pax,CRV-USDT,CRV-USDK,CRV-RSV,CRV-3Crypto,GUSD,PAX,USD,ILK,BNB,PAXG,ADA,FTT,SOL,SRM,RAY,XLM,SUSHI,CRV,BAL,AAVE,MATIC,GRT,ENJ,USDP,IOST,AMP,PERP,SHIB,ALICE,ALPHA,ANKR,ATA,AVA,AXS,BAKE,BAND,BNT,BTCST,CELR,CFX,CHR,COS,COTI,CTSI,DUSK,EGLD,ELF,FET,FLOW,FTM,INJ,IOTX,MDX,NEAR,OCEAN,ONT,POLS,REEF,WRX,XEC,XTZ,XVS,ZIL,DOT,FIL,TRX,CAKE,ADX,FIRO,SXP,ATOM,IOTA,AKRO,AUDIO,BADGER,CVC,DENT,DYDX,FORTH,GNO,HOT,LPT,LRC,NKN,NMR,NU,OGN,OXT,POLY,QNT,RLC,RSR,SAND,SKL,STMX,STORJ,TRB,UMA,DPI,VSP,CHSB,EURT,GHST,3CRV,CRVRENWBTC,MIR-UST UNI LP,ALCX,ALUSD,USDP3CRV,RENBTC,YVECRV,CVX,USDTTRC20,AUD,HKD,GBP,EUR,HUSD,HT,DASH,EURS,AVAX,BTT,GALA,ILV,APE | BTC,ETH,USDT,USDC | True | ZRX, BAT, REP, ETH, SAI, BTC, XRP, LTC, EOS, BCH, XMR, DOGE, USDC, USDT, BSV, NEO, ETC, OMG, ZEC, BTG, SAN, DAI, UNI, WBTC, COMP, LUNA, UST, BUSD, KNC, LEND, LINK, MANA, MKR, SNX, SUSD, TUSD, eCRV-DAO, HEGIC, YFI, 1INCH, CRV-IB, CRV-HBTC, BOOST, CRV-sBTC, CRV-renBTC, CRV-sAave, CRV-oBTC, CRV-pBTC, CRV-LUSD, CRV-BBTC, CRV-tBTC, CRV-FRAX, CRV-yBUSD, CRV-COMP, CRV-GUSD, yUSD, CRV-3pool, CRV-TUSD, CRV-BUSD, CRV-DUSD, CRV-UST, CRV-mUSD, sUSD, CRV-sUSD, CRV-LINK, CRV-USDN, CRV-USDP, CRV-alUSD, CRV-Aave, CRV-HUSD, CRV-EURS, RAI, CRV-triCrypto, CRV-Pax, CRV-USDT, CRV-USDK, CRV-RSV, CRV-3Crypto, GUSD, PAX, USD, ILK, BNB, PAXG, ADA, FTT, SOL, SRM, RAY, XLM, SUSHI, CRV, BAL, AAVE, MATIC, GRT, ENJ, USDP, IOST, AMP, PERP, SHIB, ALICE, ALPHA, ANKR, ATA, AVA, AXS, BAKE, BAND, BNT, BTCST, CELR, CFX, CHR, COS, COTI, CTSI, DUSK, EGLD, ELF, FET, FLOW, FTM, INJ, IOTX, MDX, NEAR, OCEAN, ONT, POLS, REEF, WRX, XEC, XTZ, XVS, ZIL, DOT, FIL, TRX, CAKE, ADX, FIRO, SXP, ATOM, IOTA, AKRO, AUDIO, BADGER, CVC, DENT, DYDX, FORTH, GNO, HOT, LPT, LRC, NKN, NMR, NU, OGN, OXT, POLY, QNT, RLC, RSR, SAND, SKL, STMX, STORJ, TRB, UMA, DPI, VSP, CHSB, EURT, GHST, 3CRV, CRVRENWBTC, MIR-UST UNI LP, ALCX, ALUSD, USDP3CRV, RENBTC, YVECRV, CVX, USDTTRC20, AUD, HKD, GBP, EUR, HUSD, HT, DASH, EURS, AVAX, BTT, GALA, ILV, APE |
| platforms | Platforms to search interest rates in separated by comma. Default: BlockFi,Ledn,SwissBorg,Youhodler. Options: MakerDao,Compound,Poloniex,Bitfinex,dYdX,CompoundV2,Linen,Hodlonaut,InstaDapp,Zerion,Argent,DeFiSaver,MakerDaoV2,Ddex,AaveStable,AaveVariable,YearnFinance,BlockFi,Nexo,CryptoCom,Soda,Coinbase,SaltLending,Ledn,Bincentive,Inlock,Bitwala,Zipmex,Vauld,Delio,Yield,Vesper,Reflexer,SwissBorg,MushroomsFinance,ElementFi,Maple,CoinRabbit,WirexXAccounts,Youhodler,YieldApp,NotionalFinance,IconFi | BlockFi,Ledn,SwissBorg,Youhodler | True | MakerDao, Compound, Poloniex, Bitfinex, dYdX, CompoundV2, Linen, Hodlonaut, InstaDapp, Zerion, Argent, DeFiSaver, MakerDaoV2, Ddex, AaveStable, AaveVariable, YearnFinance, BlockFi, Nexo, CryptoCom, Soda, Coinbase, SaltLending, Ledn, Bincentive, Inlock, Bitwala, Zipmex, Vauld, Delio, Yield, Vesper, Reflexer, SwissBorg, MushroomsFinance, ElementFi, Maple, CoinRabbit, WirexXAccounts, Youhodler, YieldApp, NotionalFinance, IconFi |

---

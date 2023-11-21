---
title: contracts
description: This page details how to effectively fetch all contract addresses for
  a specific blockchain platform with customizable parameters for limitations and
  sorting. Various platforms such as Ethereum and Bitcoin are discussed, along with
  illustration on detailed sets of commands.
keywords:
- contracts
- blockchain platform
- smart contracts
- ethereum
- bitcoin
- parameters
- sort data
- display
- crypto
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /ov/contracts - Reference | OpenBB Terminal Docs" />

Gets all contract addresses for given platform. Provide platform id with -p/--platform parameter You can display only N number of smart contracts with --limit parameter. You can sort data by id, type, active, balance --sortby parameter and also with --reverse flag to sort descending. Displays: id, type, active, balance

### Usage

```python wordwrap
contracts [-p {btc-bitcoin,eos-eos,eth-ethereum,xrp-xrp,bch-bitcoin-cash,ada-cardano,xem-nem,neo-neo,xlm-stellar,etc-ethereum-classic,qtum-qtum,vet-vechain,bts-bitshares,waves-waves,nxt-nxt,act-achain,ubq-ubiq,xcp-counterparty,ppc-peercoin,etp-metaverse-etp,signa-signa,slr-solarcoin,omni-omni,trx-tron,bnb-binance-coin,ardr-ardor,ht-huobi-token,ont-ontology,wan-wanchain,ftm-fantom,cro-cryptocom-chain,atom-cosmos,matic-polygon,cntm-connectome,one-harmony,algo-algorand,kava-kava,celo-celo,near-near-protocol,afcash-africunia-bank,avax-avalanche,sol-solana,blvr-believer,bcna-bitcanna831,fsxu-flashx-ultra,chik-chickenkebab-finance,crx-cryptex,etl-etherlite,eubi-eubi-token,swam-swapmatic-token,shells-shells,levelg-levelg,cdy-bitcoin-candy,lyr-lyra,berry-berry,drc-deracoin,vega-vega-coin,xgk-goldkash,ptd-peseta-digital,osmo-osmosis,mmt-moments-market,movr-moonriver,gems-algogems,kilt-kilt-protocol,harl-harmonylauncher,alph-alephium,ride-holoride,fcon-spacefalcon,love-diamond-love,kint-kintsugi,chum-chum-coin,polyx-polymesh,kfl-kaafila,glink-gemlink,ron-ronin-token,evmos-evmos,wtip-worktips9618,xeta-xana,arn-arenum,mart-artmeta,azit-azit,fcd-freshcut-diamond,pbt-property-blockchain-trade,fww-farmers-world-wood,cand-canary-dollar,srs-sirius-finance,arz-arize,hash-provenance-blockchain,joy-drawshop-kingdom-reverse-joystick,orbc-orbis,b3x-bnext-b3x,xmp-maptcoin,gomt-gomeat,pro-proton-coin,slrr-solarr,xgbl-xungible,pls-pulsechain,utg-ultronglow,luna-terra-v2,oxp-onxrp,algx-algodex,op-optimism,cvshot-cvshots,xspectar-xspectar,blkz-blocksworkz,sva-solvia,bdlt-bdlt,ogy-origyn-foundation,digau-dignity-gold,trx3l-trx3l,eth3s-eth3s,intr-interlay,crom-crome,tutl-tutela,cc-cloudcoin,ztg-zeitgeist,film-filmcredits,znt-zenith-finance,bnd-bened,mddn-modden234234234,wei-wei,dcrn-decred-next,omc-omchain,turn-big-turn,cmp-caduceus,pmg-pmg-coin,xx-xx-network,neer-metaversenetwork-pioneer,cic-crazy-internet-coin,mtbc-mateablecoin,bsx-basilisk,cuc-cuprum-coin,fury-fanfury,vxxl-vxxl,spex-stepex,log-logos,metal-metal-blockchain,nai-natiol,ling-lingose,wsd-whiteswap,oeth-oeth,gp-gameplace,jdc-just-dough-coin,suyoshi-suzaku-hideyoshi,babymeta-baby-meta,crotale-crotale-token,bit-bitnet,arb-arbitrum,bxr2-bitxor,bidkoyn-low-effort-coin,som3-sound-of-music,lbc-littleboycoin,dags-dagcoin,gprx-gainprox,pepew-pepepow,base-base}] [-l LIMIT] [-s {id,type,active}] [-r]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| platform | -p  --platform | Blockchain platform like eth-ethereum | eth-ethereum | True | btc-bitcoin, eos-eos, eth-ethereum, xrp-xrp, bch-bitcoin-cash, ada-cardano, xem-nem, neo-neo, xlm-stellar, etc-ethereum-classic, qtum-qtum, vet-vechain, bts-bitshares, waves-waves, nxt-nxt, act-achain, ubq-ubiq, xcp-counterparty, ppc-peercoin, etp-metaverse-etp, signa-signa, slr-solarcoin, omni-omni, trx-tron, bnb-binance-coin, ardr-ardor, ht-huobi-token, ont-ontology, wan-wanchain, ftm-fantom, cro-cryptocom-chain, atom-cosmos, matic-polygon, cntm-connectome, one-harmony, algo-algorand, kava-kava, celo-celo, near-near-protocol, afcash-africunia-bank, avax-avalanche, sol-solana, blvr-believer, bcna-bitcanna831, fsxu-flashx-ultra, chik-chickenkebab-finance, crx-cryptex, etl-etherlite, eubi-eubi-token, swam-swapmatic-token, shells-shells, levelg-levelg, cdy-bitcoin-candy, lyr-lyra, berry-berry, drc-deracoin, vega-vega-coin, xgk-goldkash, ptd-peseta-digital, osmo-osmosis, mmt-moments-market, movr-moonriver, gems-algogems, kilt-kilt-protocol, harl-harmonylauncher, alph-alephium, ride-holoride, fcon-spacefalcon, love-diamond-love, kint-kintsugi, chum-chum-coin, polyx-polymesh, kfl-kaafila, glink-gemlink, ron-ronin-token, evmos-evmos, wtip-worktips9618, xeta-xana, arn-arenum, mart-artmeta, azit-azit, fcd-freshcut-diamond, pbt-property-blockchain-trade, fww-farmers-world-wood, cand-canary-dollar, srs-sirius-finance, arz-arize, hash-provenance-blockchain, joy-drawshop-kingdom-reverse-joystick, orbc-orbis, b3x-bnext-b3x, xmp-maptcoin, gomt-gomeat, pro-proton-coin, slrr-solarr, xgbl-xungible, pls-pulsechain, utg-ultronglow, luna-terra-v2, oxp-onxrp, algx-algodex, op-optimism, cvshot-cvshots, xspectar-xspectar, blkz-blocksworkz, sva-solvia, bdlt-bdlt, ogy-origyn-foundation, digau-dignity-gold, trx3l-trx3l, eth3s-eth3s, intr-interlay, crom-crome, tutl-tutela, cc-cloudcoin, ztg-zeitgeist, film-filmcredits, znt-zenith-finance, bnd-bened, mddn-modden234234234, wei-wei, dcrn-decred-next, omc-omchain, turn-big-turn, cmp-caduceus, pmg-pmg-coin, xx-xx-network, neer-metaversenetwork-pioneer, cic-crazy-internet-coin, mtbc-mateablecoin, bsx-basilisk, cuc-cuprum-coin, fury-fanfury, vxxl-vxxl, spex-stepex, log-logos, metal-metal-blockchain, nai-natiol, ling-lingose, wsd-whiteswap, oeth-oeth, gp-gameplace, jdc-just-dough-coin, suyoshi-suzaku-hideyoshi, babymeta-baby-meta, crotale-crotale-token, bit-bitnet, arb-arbitrum, bxr2-bitxor, bidkoyn-low-effort-coin, som3-sound-of-music, lbc-littleboycoin, dags-dagcoin, gprx-gainprox, pepew-pepepow, base-base |
| limit | -l  --limit | display N number records | 15 | True | None |
| sortby | -s  --sortby | Sort by given column | id | True | id, type, active |
| reverse | -r  --reverse | Data is sorted in ascending order by default. Reverse flag will sort it in an descending way. Only works when raw data is displayed. | False | True | None |


---

## Examples

```python
2022 Feb 15, 08:16 (🦋) /crypto/ov/ $ contracts
                          Contract Addresses
┌────────────────────────────────────────────────────┬───────┬────────┐
│ id                                                 │ type  │ active │
├────────────────────────────────────────────────────┼───────┼────────┤
│ -                                                  │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ -dogeinu                                           │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ -exotix                                            │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ -onlychads                                         │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ -pcore                                             │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ -the-ether-collection                              │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0175-geely-automobile                              │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0241-alibaba-health-information-technology-limited │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0347-angang-steel                                  │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0358-jiangxi-copper                                │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0522-asm-pacific-technology-limited                │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0728-china-telecom                                 │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0753-air-china                                     │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0857-petrochina                                    │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0916-china-longyuan-power                          │ ERC20 │ True   │
└────────────────────────────────────────────────────┴───────┴────────┘
```
---

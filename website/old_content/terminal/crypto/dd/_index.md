---
title: Introduction to Cryptocurrency Due Diligence
keywords: "cryptocurrency, dd, due diligence, tokenomics, overview, bitcoin"
excerpt: "An Introduction to Cryptocurrency Due Diligence, within the Cryptocurrency Menu,
with a brief overview of the features."
geekdocCollapseSection: true
---

The Cryptocurrency Due Diligence menu gives the user the ability to delve deeper into the coin of choice. To be able to
do this, the menu offers basic information about the loaded coin (<a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/dd/info/" target="_blank" rel="noreferrer noopener">info</a>
and <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/dd/basic/" target="_blank" rel="noreferrer noopener">basic</a>), information about the project, technology details, audits etcetera
(<a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/dd/pi/" target="_blank" rel="noreferrer noopener">pi</a>), insights into the coin balance and order book
(<a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/dd/balance/" target="_blank" rel="noreferrer noopener">balance</a> and <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/dd/cbbook/" target="_blank" rel="noreferrer noopener">cbbook</a>),
the tokenomics and fundraising details
(<a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/dd/tk/" target="_blank" rel="noreferrer noopener">tk</a> and <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/dd/fr/" target="_blank" rel="noreferrer noopener">fr</a>)
and lastly, social media activity
(<a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/dd/mt/" target="_blank" rel="noreferrer noopener">mt</a>, <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/dd/twitter/" target="_blank" rel="noreferrer noopener">twitter</a>
and <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/dd/dev/" target="_blank" rel="noreferrer noopener">dev</a>).

## How to use

The Cryptocurrency Due Diligence menu is called upon by typing `dd` (after loading a coin), while inside the `crypto` menu, which opens the following menu:

![Cryptocurrency Due Diligence menu](https://user-images.githubusercontent.com/46355364/178734389-dcee7a96-bb57-42fb-ad8e-13f27662e03b.png)

This menu requires you to load a coin with the `load` command. Thus, alternatively, you can also type `/crypto/load BTC/dd`.
Within the Cryptocurrency Due Diligence menu you can find features examining an extensive amount of metrics about the
loaded coin. As an example, you can see the latest trades done on the loaded coin with `trades`:

```
2022 Jul 13, 07:42 (🦋) /crypto/dd/ $ trades

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━┓
┃ time                        ┃ price          ┃ size       ┃ side ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━┩
│ 2022-07-13T11:42:29.451817Z │ 19832.40000000 │ 0.00100000 │ buy  │
├─────────────────────────────┼────────────────┼────────────┼──────┤
│ 2022-07-13T11:42:04.137456Z │ 19831.63000000 │ 0.00298698 │ buy  │
├─────────────────────────────┼────────────────┼────────────┼──────┤
│ 2022-07-13T11:41:28.752991Z │ 19843.96000000 │ 0.00006215 │ sell │
├─────────────────────────────┼────────────────┼────────────┼──────┤
│ 2022-07-13T11:40:24.579004Z │ 19850.63000000 │ 0.05000000 │ sell │
├─────────────────────────────┼────────────────┼────────────┼──────┤
│ 2022-07-13T11:40:14.66834Z  │ 19848.15000000 │ 0.15000000 │ buy  │
├─────────────────────────────┼────────────────┼────────────┼──────┤
│ 2022-07-13T11:39:39.203275Z │ 19854.85000000 │ 0.00006226 │ sell │
├─────────────────────────────┼────────────────┼────────────┼──────┤
│ 2022-07-13T11:39:31.308755Z │ 19860.14000000 │ 0.06606458 │ sell │
├─────────────────────────────┼────────────────┼────────────┼──────┤
│ 2022-07-13T11:39:31.308755Z │ 19857.07000000 │ 0.00000379 │ sell │
├─────────────────────────────┼────────────────┼────────────┼──────┤
│ 2022-07-13T11:39:21.693412Z │ 19857.07000000 │ 0.00027000 │ sell │
├─────────────────────────────┼────────────────┼────────────┼──────┤
│ 2022-07-13T11:38:56.195803Z │ 19848.41000000 │ 0.00100108 │ buy  │
├─────────────────────────────┼────────────────┼────────────┼──────┤
│ 2022-07-13T11:38:46.766487Z │ 19848.72000000 │ 0.00127984 │ sell │
├─────────────────────────────┼────────────────┼────────────┼──────┤
│ 2022-07-13T11:38:46.766487Z │ 19848.71000000 │ 0.00057219 │ sell │
├─────────────────────────────┼────────────────┼────────────┼──────┤
│ 2022-07-13T11:38:46.766487Z │ 19848.70000000 │ 0.00108236 │ sell │
├─────────────────────────────┼────────────────┼────────────┼──────┤
│ 2022-07-13T11:38:46.766487Z │ 19848.69000000 │ 0.00077974 │ sell │
├─────────────────────────────┼────────────────┼────────────┼──────┤
│ 2022-07-13T11:38:46.766487Z │ 19848.68000000 │ 0.00082548 │ sell │
└─────────────────────────────┴────────────────┴────────────┴──────┘
```

## Examples

To get an understanding of the coin we are looking at, it is possible to look into some basic information with `basic`:

```
2022 Jul 13, 07:45 (🦋) /crypto/dd/ $ basic

                                    Basic Coin Information
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric      ┃ Value                                                                         ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ id          │ btc-bitcoin                                                                   │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ name        │ Bitcoin                                                                       │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ symbol      │ BTC                                                                           │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ rank        │ 1                                                                             │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ type        │ coin                                                                          │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ description │ Bitcoin is a cryptocurrency and worldwide payment system. It is the first     │
│             │ decentralized digital currency, as the system works without a central bank or │
│             │ single administrator.                                                         │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ proof_type  │ Proof of Work                                                                 │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ tags        │ Segwit, Cryptocurrency, Proof Of Work, Payments, Sha256, Mining, Lightning    │
│             │ Network                                                                       │
└─────────────┴───────────────────────────────────────────────────────────────────────────────┘
```

Then, we have the option to look into the project information with `pi`. Note that this requires an API Key from Messari which you
can find more information about <a href="https://openbb-finance.github.io/OpenBBTerminal/#accessing-other-sources-of-data-via-api-keys" target="_blank" rel="noreferrer noopener">here</a>.
This command returns the following:

```
2022 Jul 13, 07:51 (🦋) /crypto/dd/ $ pi

                                                                                                                                BTC General Info
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric             ┃ Value                                                                                                                                                                                                                                                   ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Project Details    │ Bitcoin is the first distributed consensus-based censorship-resistant, permissionless, peer-to-peer payment settlement network with a provably scarce, programmable, native currency.                                                                   │
│                    │ Bitcoin (BTC), the native asset of the Bitcoin blockchain, is the world's first digital currency without a central bank or administrator. The Bitcoin network is an emergent decentralized monetary institution that exists through the interplay       │
│                    │ between full nodes, miners, and developers. It is set by a social contract that is created and opted into by the users of the network and hardened                                                                                                      │
│                    │ through >game theory and cryptography. Bitcoin is the first, oldest, and largest cryptocurrency in the world.                                                                                                                                           │
├────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Technology Details │ "Bitcoin" is a label used for a protocol and a currency.                                                                                                                                                                                                │
│                    │                                                                                                                                                                                                                                                         │
│                    │ Bitcoin, the currency, is bits of data usable outside the limitations of the protocol using second-layer solutions like <a href="https://messari.io/resource/lightning-network">Lightning Network</a> payment channels.                                 │
│                    │                                                                                                                                                                                                                                                         │
│                    │ Bitcoin, the protocol, is a distributed, time-stamped ledger of <a href="https://messari.io/resource/utxo">unspent transaction output</a> (UTXO) transfers stored in an append-only chain of 1MB data blocks. A network of mining and economic <a       │
│                    │ href="https://messari.io/resource/node">nodes</a> maintains this ledger by validating, propagating, and fighting to include <a href="https://messari.io/resource/mempool">mempool</a> transactions in new blocks. Economic nodes (aka "full nodes")     │
│                    │ receive transactions from other network participants, validate them against network consensus rules and double-spend vectors, and propagate the transactions to other full nodes that also validate and propagate. Valid transactions are sent to the   │
│                    │ network's mempool waiting for mining nodes to confirm them via inclusion in the next block.                                                                                                                                                             │
│                    │                                                                                                                                                                                                                                                         │
│                    │ Mining nodes work to empty the mempool usually in a highest-to-lowest fee order by picking transactions to include in the next block and racing against each other to generate a hash less than the target number set by Bitcoin's difficulty           │
│                    │ adjustment algorithm. Bitcoin uses a Proof-of-Work (PoW) consensus mechanism to establish the chain of blocks with the most accumulated “work” (a.k.a., energy spent on solved hashes) as the valid chain. Other network peers can cheaply verify the   │
│                    │ chain’s work.                                                                                                                                                                                                                                           │
│                    │                                                                                                                                                                                                                                                         │
│                    │ Mining difficulty regularly adjusts to maintain Bitcoin's average ten-minute block schedule. Mining nodes add new blocks to whatever chain has the largest accumulated proof of work maintained by a network of economic nodes with downloaded copies   │
│                    │ of the same chain.                                                                                                                                                                                                                                      │
│                    │                                                                                                                                                                                                                                                         │
│                    │ Learn More:                                                                                                                                                                                                                                             │
│                    │ Bitcoin Developer's Guide                                                                                                                                                                                                                               │
│                    │ Mastering Bitcoin                                                                                                                                                                                                                                       │
└────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

                            BTC Public Repositories
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Name                    ┃ Link                               ┃ License_type ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Bitcoin Core Repository │ https://github.com/bitcoin/bitcoin │ MIT License  │
└─────────────────────────┴────────────────────────────────────┴──────────────┘

                                                                                                                              BTC Vulnerabilities
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Title                           ┃ Date                      ┃ Type      ┃ Details                                                                                                                                                                                            ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Value Overflow Incident         │ 2010-08-06 04:00:00+00:00 │ Inflation │ On 6 August 2010, a major vulnerability in the bitcoin protocol was spotted. Transactions weren't properly verified before they were included in the transaction log or blockchain, which let      │
│                                 │                           │           │ users bypass bitcoin's economic restrictions and create an indefinite number of bitcoins. On 15 August, the vulnerability was exploited; over 184 billion bitcoins were generated in a transaction │
│                                 │                           │           │ and sent to two addresses on the network. Within hours, the transaction was spotted and erased from the transaction log after the bug was fixed and the network forked to an updated version of    │
│                                 │                           │           │ the bitcoin protocol. This was the only major security flaw found and exploited in bitcoin's history.                                                                                              │
├─────────────────────────────────┼───────────────────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Denial of Service Vulnerability │ 2018-09-20 04:00:00+00:00 │ Inflation │ On September 17, Bitcoin Core developers discovered that older versions of Bitcoin Core will crash if they try to process a block containing a transaction that attempts to spend the same input   │
│                                 │                           │           │ twice. Such blocks are invalid, so they can only be created by a miner willing to sacrifice their allowed income for creating a block of at least 12.5 BTC (about $80,000 USD as of this writing). │
│                                 │                           │           │                                                                                                                                                                                                    │
│                                 │                           │           │ Soon after discovering the DDoS attack vulnerability, Bitcoin Core developers also discovered an inflation bug which they quickly determined had the same root cause and fix. They decided to      │
│                                 │                           │           │ disclose the DDoS vulnerability immediately while keeping the inflation bug quiet. This provided developers time to reach out to miners, businesses, and other affected systems about upgrading    │
│                                 │                           │           │ their software, while also providing additional time to fix the exploit.                                                                                                                           │
│                                 │                           │           │                                                                                                                                                                                                    │
│                                 │                           │           │ https://bitcoincore.org/en/2018/09/18/release-0.16.3/                                                                                                                                              │
│                                 │                           │           │ https://bitcoincore.org/en/2018/09/20/notice/                                                                                                                                                      │
└─────────────────────────────────┴───────────────────────────┴───────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Looking ahead, we can use the command (coming from the same source) `rm` which discusses plans for the future. E.g.
if we load in `ETH` with `load ETH` and use `rm` we receive the following:

```
2022 Jul 13, 07:57 (🦋) /crypto/dd/ $ rm

                                                                                                                                  ETH Roadmap
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Title                                     ┃ Date       ┃ Type              ┃ Details                                                                                                                                                                                         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Serenity Phase 0                          │ 2020-12-01 │ Network Launch    │ Serenity Phase 0 marks Ethereum's initial transition to Ethereum 2.0. This initial phase will introduce the Beacon Chain, which will serve as the backbone for Ethereum 2.0's sharded network   │
│                                           │            │                   │ architecture. As opposed to Ethereum's current Proof-of-Work (PoW) blockchain, the Beacon Chain will use Casper FFG, a specific variation of Proof-of-Stake (PoS), and a system of validators   │
│                                           │            │                   │ to confirm transactions and inhibit Sybil attacks.                                                                                                                                              │
│                                           │            │                   │                                                                                                                                                                                                 │
│                                           │            │                   │ Ethereum core developers split the Serenity upgrade into three phases to optimize the development process and limit deployment risks. The specifications for this first phase include:          │
│                                           │            │                   │ Beacon Chain is the core of the Ethereum 2.0 system; it manages the PoS protocol for itself and all of the individual shard chains. The Beacon chain will use Casper the Friendly Finality      │
│                                           │            │                   │ Gadget (Casper FFG) to ensure transaction finality.                                                                                                                                             │
│                                           │            │                   │ Fork Choice enables validators' clients to automatically select the right chain when the Phase 0 Serenity fork is initiated                                                                     │
│                                           │            │                   │ Deposit Contract allows Ethereum stakeholders to transfer funds from ETH 1.0 to ETH 2.0 and claim rights to a validator role on the new PoS chain                                               │
│                                           │            │                   │ Honest Validator dictates the expected behavior of an "honest validator and slashing specifications with respect to Phase 0 of ETH 2.0                                                          │
│                                           │            │                   │                                                                                                                                                                                                 │
│                                           │            │                   │ It is essential to note the launch of Phase 0 will not immediately replace Ethereum 1.0 (also known as Ethereum 1.x). The two chains will coexist for at least until Serenity Phase 1.5         │
│                                           │            │                   │ arrives, which marks when the current Ethereum chain will merge into the Ethereum 2.0 system a shard within the network. Running the legacy and future chains in parallel may cause ETH         │
│                                           │            │                   │ inflation to increase as both chains will simultaneously mint new tokens.                                                                                                                       │
├───────────────────────────────────────────┼────────────┼───────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Muir Glacier                              │ 2020-01-02 │ Hard Fork Upgrade │ The Muir Glacier hard fork activated at block 9,200,000, which arrived on Jan. 2, 2020. The upgrade only included EIP-2384, which delayed Ethereum's inherent "Difficulty Bomb" for another     │
│                                           │            │                   │ 4,000,000 blocks (approximately 611 days) to prevent block times from increasing (and usability plummeting). Muir Glacier's abrupt arrival, less than a month after Istanbul, marked the third  │
│                                           │            │                   │ time Ethereum core developers opted to delay the Difficulty Bomb (aka Ice Age).                                                                                                                 │
│                                           │            │                   │                                                                                                                                                                                                 │
│                                           │            │                   │ Learn more:                                                                                                                                                                                     │
│                                           │            │                   │ Ethereum Muir Glacier Upgrade by the Ethereum Cat Herders                                                                                                                                       │
├───────────────────────────────────────────┼────────────┼───────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Istanbul (Phase I)                        │ 2019-12-07 │ Hard Fork Upgrade │ The first phase of Istanbul is set to activate at block 9,069,000, almost two months after its initially scheduled launch (Oct. 16, 2019). Istanbul Phase I intends to introduce six new EIPs   │
│                                           │            │                   │ upon activation to help optimize opcode computational costs, improve denial-of-service attack security, and enhance the performance of layer-2 solutions using a                                │
│                                           │            │                   │ href="https://messari.io/article/zk-snark"ZK-SNARKs/a or a href="https://messari.io/article/zk-stark"ZK-STARKs/a, among other advancements. The accepted EIPs include:                          │
│                                           │            │                   │ EIP-152 adds the ability to verify Zcash-to-Ethereum atomic swaps                                                                                                                               │
│                                           │            │                   │ EIP-1108 reduces the costs for ZK-SNARKs                                                                                                                                                        │
│                                           │            │                   │ EIP-1344 improves smart contract ability, especially those used by layer-2 solutions, to track the correct base chain during a hard fork                                                        │
│                                           │            │                   │ EIP-1844 restructures the costs of specific a href="https://messari.io/article/ethereum-virtual-machine"Ethereum Virtual Machine (EVM)/a opcodes to deter spamming attacks and to match each    │
│                                           │            │                   │ operation with its required level of computation                                                                                                                                                │
│                                           │            │                   │ EIP-2028 reduces the cost of calling data within transactions and the fees associated with ZK-SNARKs and ZK-STARKs                                                                              │
│                                           │            │                   │ EIP-2200 alters the cost of storage in the EVM and allows smart contracts to generate more creative functions                                                                                   │
│                                           │            │                   │                                                                                                                                                                                                 │
├───────────────────────────────────────────┼────────────┼───────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Metropolis: Constantinople/St. Petersburg │ 2019-02-28 │ Hard Fork Upgrade │ Constantinople, the second phase of Metropolis, was initially scheduled to go live at block 7,080,000 (January 16, 2019). But on January 15, 2019, security auditing firm ChainSecurity         │
│                                           │            │                   │ discovered a vulnerability in one of the accepted EIPs that would enable a reentrancy attack (i.e., the opportunity for an attacker to steal user funds similar to The DAO hack). Core Ethereum │
│                                           │            │                   │ developers and some projects running on the network voted to delay Constantinople until the developers closed the security loophole.                                                            │
│                                           │            │                   │                                                                                                                                                                                                 │
│                                           │            │                   │ After a month-long delay, Constantinople and its security patch, St. Petersburg, went live at block 7,280,000, introducing five new code changes to the network:                                │
│                                           │            │                   │ EIP-145 added Bitwise shifting instructions to the EVM, making the execution of shifts in smart contracts significantly cheaper                                                                 │
│                                           │            │                   │ EIP-1052 expedited inter-smart contract verification (smart contract can verify each other via a hash rather than the entire code set)                                                          │
│                                           │            │                   │ EIP-1014 improved state channel integrations to facilitate the connection to off-chain scaling solutions                                                                                        │
│                                           │            │                   │ EIP-1283 reduced costs for executing multiple updates within a single transaction (aka the SSTORE opcode)                                                                                       │
│                                           │            │                   │ EIP-1234 delayed the difficulty bomb for another year and reduced the mining reward from three to two ETH per block (the reduction is also known as the "Thirdening")                           │
│                                           │            │                   │                                                                                                                                                                                                 │
├───────────────────────────────────────────┼────────────┼───────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Metropolis: Byzantium                     │ 2017-10-16 │ Hard Fork Upgrade │ Byzantium was the first phase of the proposed Metropolis upgrade and activated at block 4,370,000. The Byzantium hard fork included nine EIPs, with EIP-100, EIP-658, and EIP-649, introducing  │
│                                           │            │                   │ the most significant code changes.                                                                                                                                                              │
│                                           │            │                   │ EIP-100 adjusted the difficulty formula to stabilize the ETH issuance rate                                                                                                                      │
│                                           │            │                   │ EIP-658 added a new field to transaction receipts to indicate success or failure                                                                                                                │
│                                           │            │                   │ EIP-649 delayed the difficulty bomb (i.e., the Ethereum "ice age") by one year and reduced the block subsidy from five to three ETH                                                             │
│                                           │            │                   │ Details on the remaining Byzantium EIPs are available here.                                                                                                                                     │
│                                           │            │                   │                                                                                                                                                                                                 │
└───────────────────────────────────────────┴────────────┴───────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

As well as a graph that depicts price movements after these announcements.

![price movements ETH](https://user-images.githubusercontent.com/46355364/178734435-175181e3-a0fe-403c-b59c-c80ee70f6078.png)

Lastly, keeping the ETH coin loaded, we can also look at some sentiment analysis by acquiring the different sentiment
scores with `score` as follows:

```
2022 Jul 13, 08:00 (🦋) /crypto/dd/ $ score

        Different Scores for Loaded Coin
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Metric                          ┃ Value      ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Coingecko Rank                  │ 2.00       │
├─────────────────────────────────┼────────────┤
│ Coingecko Score                 │ 75.87      │
├─────────────────────────────────┼────────────┤
│ Developer Score                 │ 97.43      │
├─────────────────────────────────┼────────────┤
│ Community Score                 │ 58.56      │
├─────────────────────────────────┼────────────┤
│ Liquidity Score                 │ 96.88      │
├─────────────────────────────────┼────────────┤
│ Sentiment Votes Up Percentage   │ 58.29      │
├─────────────────────────────────┼────────────┤
│ Sentiment Votes Down Percentage │ 41.71      │
├─────────────────────────────────┼────────────┤
│ Public Interest Score           │ 0.31       │
├─────────────────────────────────┼────────────┤
│ Facebook Likes                  │            │
├─────────────────────────────────┼────────────┤
│ Twitter Followers               │ 2673876.00 │
├─────────────────────────────────┼────────────┤
│ Reddit Average Posts 48H        │ 3.11       │
├─────────────────────────────────┼────────────┤
│ Reddit Average Comments 48H     │ 71.44      │
├─────────────────────────────────┼────────────┤
│ Reddit Subscribers              │ 1340239.00 │
├─────────────────────────────────┼────────────┤
│ Reddit Accounts Active 48H      │ 972.00     │
├─────────────────────────────────┼────────────┤
│ Telegram Channel User Count     │            │
├─────────────────────────────────┼────────────┤
│ Alexa Rank                      │ 8793.00    │
├─────────────────────────────────┼────────────┤
│ Bing Matches                    │            │
└─────────────────────────────────┴────────────┘
```

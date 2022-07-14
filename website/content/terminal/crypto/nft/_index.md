---
title: Introduction to Non Fungible Token (NFT)
keywords: "cryptocurrency, nft, Non Fungible Token, tokenomics, digital asset, art"
excerpt: "An Introduction to Non Fungible Token (NFT), within the Cryptocurrency Menu,
with a brief overview of the features."
geekdocCollapseSection: true
---

The Non Fungible Token (NFT) menu gives the user the ability to delve deeper into today's NFT drops (<a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/nft/today/" target="_blank">today</a>),
upcoming and ongoing NFT drops (<a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/nft/upcoming/" target="_blank">upcoming</a> and <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/nft/ongoing/" target="_blank">ongoing</a>)
as well as statistics about certain NFTs (<a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/nft/stats/" target="_blank">stats</a>).

## How to use

The Non Fungible Token (NFT) menu is called upon by typing `nft`, while inside the `crypto` menu, which opens the following menu:

![Non Fungible Token (NFT) menu](https://user-images.githubusercontent.com/46355364/178734682-24b58a33-ae3d-4ef9-9f07-44fe713f6f16.png)

Alternatively, you can also type `/crypto/nft`. Within the Non Fungible Token (NFT) menu you can find upcoming NFTs
and explore the statistics of specific NFTs you are interested in. For example, today's NFT drops are as follows:

```
2022 Jul 13, 08:05 (🦋) /crypto/nft/ $ today

Aug 03, 2022 – Aug 10, 2022 - Crypto Legends
https://nftcalendar.io/event/crypto-legends/
My name is Vicky, I´m 12 years old and my hobbies are design and video games, my inspiration to create my collection was Genshin Impact, I have created 10,000 digital...

Jul 10, 2022 – Jul 17, 2022 - Modern Poker Club
https://nftcalendar.io/event/modern-poker-club/
PUBLIC SALE for NFT mansions Pass.
277/777 minted in WL already
Only 5 listed on opensea very solid community
http://mansionpass.com <------ to MintOnly .039 ETH per mint  20 max...

Jun 22, 2022 – Jul 22, 2022 - Azuki Demon - Minting is Live
https://nftcalendar.io/event/azuki-demon-minting-is-live/
Croatian startup Revuto, which provides users with control over their subscriptions, has announced its entrance into the NFT realm. The never-before-seen initiative, dubbed Revulution NFT, enables minters to...

Jul 13, 2022 – Jul 20, 2022 - Street Chicks
https://nftcalendar.io/event/street-chicks/
Minting is Live,
Mint Price: 0.036 ETH
6666 Mutant CloneX make their ways into the Metaverse. Each and every one of our loyal holders of Mutant CloneX...

Jul 13, 2022 – Jul 20, 2022 - NFT Mansions - Public Sale
https://nftcalendar.io/event/public-sale-1/
9999 fighting fish living on the BNB Chain. FFC owners will have access to members-only areas. FFC are not only fun using as PFP, but also the owners will have...
```

## Examples

To find out which NFTs are dropping in the near future, you have the ability to use `upcoming` (limiting to 3 items with `-l`):

```
2022 Jul 13, 08:08 (🦋) /crypto/nft/ $ upcoming -l 3
Jul 13, 2022 – Jul 20, 2022 - Dracula's Land Pre-sale
https://nftcalendar.io/event/draculas-land-5-nft-private-resort-pre-sale/
On July 14th, we are launching our first NFT collection that will bring our popular collectable Christmas ornaments to the metaverse. A few highlights of this collection are listed...

Jul 14, 2022 – Jul 21, 2022 - Wendell August: Christmas in July
https://nftcalendar.io/event/wendell-august-christmas-in-july/
The second phase of the Toxix Skull Club NFT collection of 9999 Toxic Skulls!

Jul 14, 2022 – Jul 21, 2022 - Toxic Skull Club Phase 2
https://nftcalendar.io/event/toxic-skull-club-phase-2/
At Zenogakki, we aim to revolutionise the anime industry.
Animators and creatives worldwide are not credited enough when anime series are made. They work in an industry with minimal pay...
```

You can also look in the newest NFTs that have been released with `newest`:

```
2022 Jul 13, 08:09 (🦋) /crypto/nft/ $ newest
Jul 13, 2022 – Jul 20, 2022 - NFT Mansions - Public Sale
https://nftcalendar.io/event/public-sale-1/
PUBLIC SALE for NFT mansions Pass.
277/777 minted in WL already
Only 5 listed on opensea very solid community
http://mansionpass.com <------ to MintOnly .039 ETH per mint  20 max...

Jul 14, 2022 – Jul 20, 2022 - Stranger Things NFT Posters by Netflix x Candy Digital
https://nftcalendar.io/event/stranger-things-nft-posters-by-netflix-and-candy-digital/
The video streaming giant and filmmaker Netflix is celebrating the launch of the fourth season of its flagship Stranger Things series by dropping a themed NFT collection. To...

Jul 18, 2022 – Jul 25, 2022 - Perfume NFT Collection by Fvckrender and DS & Durga
https://nftcalendar.io/event/perfume-nft-collection-by-fvckrender-ds-and-durga/
While most top-rated fashion and beauty brands have already entered the web3 realm, perfume companies aren't willing to drag behind. One of the latest fragrance brands to jump...

Jul 20, 2022 – Jul 27, 2022 - Hero Drop - Phase 1
https://nftcalendar.io/event/hero-drop-phase-1/
The revolution has begun... Its time to welcome HEROES to the blockchain.
*Hero/Fire Keys required to claim.
https://hedgeheroes.io/fire-key

Jul 21, 2022 – Jul 28, 2022 - Pour My Heart - by Face of the River
https://nftcalendar.io/event/pour-my-heart-by-face-of-the-river/
“Pour My Heart” - 1st NFT drop by visual artist Face of the River. Having spent many years using real paint on canvas, this collection represents my personal transition from...
```

Lastly, we can look into the statistics of a specific NFT once you know the slug (e.g. <a href="https://opensea.io/collection/mutant-ape-yacht-club" target="_blank">mutant-ape-yacht-club</a>)
with `stats` as follows:

```
2022 Jul 13, 08:10 (🦋) /crypto/nft/ $ stats mutant-ape-yacht-club

                     Collection Stats
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                         ┃ Value                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Name                           │ Mutant Ape Yacht Club │
├────────────────────────────────┼───────────────────────┤
│ Floor Price (ETH)              │ 19.70                 │
├────────────────────────────────┼───────────────────────┤
│ Number of Owners               │ 13029.00              │
├────────────────────────────────┼───────────────────────┤
│ Market Cap (ETH)               │ 404479.49             │
├────────────────────────────────┼───────────────────────┤
│ Average Price ETH              │ 12.91                 │
├────────────────────────────────┼───────────────────────┤
│ One day volume (ETH)           │ 300.75                │
├────────────────────────────────┼───────────────────────┤
│ One day change (%)             │ -36.10                │
├────────────────────────────────┼───────────────────────┤
│ One day sales (ETH)            │ 14.00                 │
├────────────────────────────────┼───────────────────────┤
│ One day average price (ETH)    │ 21.48                 │
├────────────────────────────────┼───────────────────────┤
│ Thirty day volume (ETH)        │ 18341.20              │
├────────────────────────────────┼───────────────────────┤
│ Thirty day change (%)          │ 18.40                 │
├────────────────────────────────┼───────────────────────┤
│ Thirty day sales (ETH)         │ 959.00                │
├────────────────────────────────┼───────────────────────┤
│ Thirty day average price (ETH) │ 19.13                 │
├────────────────────────────────┼───────────────────────┤
│ Total Supply (ETH)             │ 19424.00              │
├────────────────────────────────┼───────────────────────┤
│ Total Sales (ETH)              │ 33412.00              │
├────────────────────────────────┼───────────────────────┤
│ Total Volume (ETH)             │ 431381.31             │
├────────────────────────────────┼───────────────────────┤
│ Creation Date                  │ Aug 29, 2021          │
├────────────────────────────────┼───────────────────────┤
│ URL                            │ -                     │
└────────────────────────────────┴───────────────────────┘
```

---
title: Introduction to the Government Menu
keywords: "Government, house, senate, politician, lobby, lobbyist, contract, contractor, spending, budget, treasury, trading, buys, sells, ticker, tickers, companies, listing, exchange"
date: "2022-06-02"
type: guides
status: publish
excerpt: "This guide introduces the Government submenu, within the Stocks menu, by briefly explaining the features and how to use them, showing examples in context."
geekdocCollapseSection: true
---

The features in this menu are intended to show the reported trades of elected officials, lobbyist activity, awarded contracts, and general spending of the United States Treasury Department. This menu only covers the USA, or companies that trade on US exchanges. The information in this menu is compiled by <a href="https://quiverquant.com" target="_blank">QuiverQuant</a>. 

A ticker is not required to enter the menu; navigate there from anywhere in the terminal with absolute path jumping: `/stocks/gov`

![The Government Menu](https://user-images.githubusercontent.com/85772166/173205843-1d9d5679-df73-4ec3-8b98-937f38ccac35.png)

<h2>How to use the Government Menu</h2>

The menu is divided into two sections. Features under the `Explore:` do not depend on individual tickers, while the commands listed under `Ticker:` do. Entering `lasttrades` will return a table with the five most recent days of reported trades made by Congress members. 

![Last trades from Congress](https://user-images.githubusercontent.com/85772166/173205858-c2b8ccc7-8bf3-4443-bfe1-9364b5397e16.png)

`lasttrades senate` & `lasttrades house` will other elected officials.

![Last trades posted from the Senate and the House](https://user-images.githubusercontent.com/85772166/173205867-93390576-e6f0-443b-aa0a-e5703fedb0e3.png)

`toplobbying` brings up a bar graph of recent big spenders on K Street, that are listed on-exchange. The optional arguments `l`, `--raw` & `--export` changes the number of companies returned, shows a table of the raw data, or exports the data to a file.

![Top ten companies actively lobbying the US government](https://user-images.githubusercontent.com/85772166/173206158-bd42523c-50de-4f44-b1b5-7012cadc44a2.png)

The trivial spending by government can be tracked with the command, `lastcontracts`. Screwdrivers, furniture, bath towels; keep tabs on where those tax dollars are spent.

![The latest agency line items to be reported](https://user-images.githubusercontent.com/85772166/173206164-a76b89f1-23fb-4ef1-ae0d-b1e7989f12ea.png)

`load` a specific ticker to activate the lower features.

<h2>Examples</h2>

Microsoft is a favourite in Washington; `gtrades` shows the bullish or bearish tendencies of elected officials over time.

![Microsoft trades by elected officials](https://user-images.githubusercontent.com/85772166/173206175-e6b0436a-82cd-4075-b4bf-87926db0a31e.png)

A table of this chart, with representatives' names, is called by adding the `--raw` flag to the command string.

![Respresentatives and their recent MSFT transactions](https://user-images.githubusercontent.com/85772166/173206186-bb8e3200-b596-49d7-b4b8-5037e62f071a.png)

A breakdown of single-issue items the company is lobbying for will be printed by the command, `lobbying`:

````
(🦋) /stocks/gov/ $ lobbying
2022-05-31: MICROSOFT CORP $30000
        Cascadia High Speed Rail Funding opportunities.   High-skilled immigration reform   Energy efficiency; climate change issues and sustainability   Cyber Security, including protecting elections   Competition policy; supply chain issues.   Workforce development issues; skilling; H.R. 1735, To provide a temporary safe harbor for publishers of online content to collectively negotiate with dominant online platforms regarding the terms on which content may be distributed.   Broadband connectivity; artificial intelligence.   Computer science education   Privacy--intelligence and surveillance.

2022-05-26: MICROSOFT CORPORATION $50000
        Tax reform   ECPA, CS for Al, STEM, TV White Spaces, Ariband, Rural Broadband   Warrants, Surveillance EPCA, Cyber Security   Cyber Security, Bulk Data collection, Surveillance, ECPA, Lawful Access   High Skilled immigration, Immigration reform, DACA

2022-05-13: MICROSOFT $15000
        Issues related to potential VISA reform.   The role of technology in defense. Innovations ability to strengthen national security.   Broadband connectivity and access. Defense technology issues.

2022-05-02: CORNERSTONE GOVERNMENT AFFAIRS OBO MICROSOFT CORPORATION $0

2022-04-20: MICROSOFT CORPORATION $70000
        S.1260, United States Innovation and Competition Act of 2021, Workforce training issues H.R.4521, America COMPETES Act of 2022, Workforce training issues Workforce Innovation and Opportunity Act, Workforce training issues   Cyber Security Work Force S.1260, United States Innovation and Competition Act of 2021, Computer Science Education H.R.4521, America COMPETES Act of 2022, Computer Science Education   Workforce issues, generally Computer Science Education

2022-04-20: MICROSOFT CORPORATION $0

2022-04-20: MICROSOFT CORPORATION $0

2022-04-20: MICROSOFT CORPORATION $50000
        Privacy; broadband infrastructure adoption and deployment; trade; sustainability education; H.R. John Lewis Voting Rights Advancement Act; Cybersecurity; NDAA; criminal justice reform.

2022-04-20: MICROSOFT CORPORATION $30000
        Monitor possible legislation to provide state tax relief for employees stranded outside their home state by COVID.   Monitor postal reform.   Monitor issues relating to trade agreements.   Monitor cybersecurity legislation. Monitor privacy oversight issues. Monitor issues relating to use of TV white space spectrum.   Monitor H1-B Visas. Monitor issues relating to high-skilled immigration.   Monitor software piracy, counterfeiting, and protection of intellectual property rights. Monitor patent reform.   Competitiveness in the online advertising and software markets. Competitiveness and the high tech sector. Monitor issues related to government access to customer data. Monitor Cloud computing issues. Monitor STEM education legislation. Monitor issues relating to data breach legislation and data breaches. Monitor issues relating to artificial intelligence. Monitor issues relating to facial recognition technology. Monitor issues relating election security technology. Monitor issues relating to Section 230 of the Communications Decency Act.

2022-04-20: MICROSOFT CORPORATION $0
````

The consistency of quarterly contract awards over time is reflected in a chart requested by the command, `histcont`

![History of Quarterly Contracts Awarded to MSFT](https://user-images.githubusercontent.com/85772166/173206200-347aef6e-6b27-4bf8-9422-c03c5b414361.png)

The ten most purchased and sold stocks amongst Senate Representatives, `topsells senate` & `topbuys senate`:

![Senate's Most Bought and Sold Stocks](https://user-images.githubusercontent.com/85772166/173206214-964bfe40-a72c-4833-8cc1-a803bba97c6e.png)

To play a demonstration in the OpenBB Terminal of the features presented in this guide, execute the routine file, `gov_demo.openbb`, from the Home Menu. 

![Playing the demonstration file to this guide](https://user-images.githubusercontent.com/85772166/173206226-2519d9ae-07b7-4cc7-b8a6-17c514c0d1df.png)

Back to the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">Introduction to Stocks Guide</a>.

---
title: Introduction to ENTER_MENU_NAME_HERE
keywords: "ENTER_KEY_WORD_HERE, ENTER_KEY_WORD_HERE, ENTER_KEY_WORD_HERE, ENTER_KEY_WORD_HERE"
date: "YEAR-MONTH-DAY"
type: our story
status: publish
excerpt: "The Introduction to ENTER_MENU_NAME_HERE explains how to use the 
ENTER_MENU_NAME_HERE and provides a brief description of its sub-menus"
---

**Important Rules**

Each page should always take the following rules in mind:
- We take a neutral position for everything we show. We don’t say things like ‘This is a good way to’ or ‘This is the gold standard’ or anything similar. These guides are not meant for any form of financial advice, conclusions or perceptions of the market. That is what we can use any social media platform for and write on your own account.
- The page is formal. We don’t include any type of jokes, memes or sarcasm/rhetoric comments. 
- We do not explain any financial term but refer to a different source, e.g. Investopedia.
- The purpose of the guide is not to educate the user about how to invest but to explain how to navigate a menu.

**General Formatting**

- Every link should open a new page (`_blank`). So use: `<a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/options/exp/" target="_blank">exp</a>`
- Some methods to format images:
  - Side by side: `<img src="image1.png" width="425"/> <img src="image2.png" width="425"/>`
  - Text and image:
    ```
    <table border="0">
     <tr>
        <td><b style="font-size:30px">TEXT TITLE</b></td>
        <td><b style="font-size:30px">IMAGE TITLE</b></td>
     </tr>
     <tr>
        <td>TEXT</td>
        <td>IMAGE</td>
     </tr>
    </table>
    ```
  - No formatting in particular: `![image](link/to/image)`
_____

<h1>Introduction to ENTER_MENU_NAME_HERE</h1>
The purpose of the menu, providing very factual information with a neutral view. E.g. "The Stocks menu is used to 
gain insights in the asset class stocks via various areas like fundamental, behavioural and technical analysis"

<h2>How to use</h2>
Explain in detail how to use the menu. Sticking with the Stocks menu, you would want to understand how to <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/search/" target="_blank">search</a> and <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/load/" target="_blank">load</a> a 
ticker, how you can show the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/candle/" target="_blank">candle</a> and how to explore various different menus. <br></br>

Make sure that you link to the Hugo documentation for each command you mention here so people can view in more detail 
how the command works exactly. Make use of HTML here so the guides page on the website doesn't close down.

<h2>Sub-menus available</h2>
Provide a brief description of each menu available and include a link to that menu. E.g, the option menu could 
have the following:

- <a href="//" target="_blank">Introduction to Fundamental Analysis</a>: gives information about the Fundamentals of the chosen ticker.
- <a href="//" target="_blank">Introduction to Behavioural Analysis</a>: gives the abilities to discover how different social media platforms view the chosen company.

It could be that these menus are so small that it makes sense to include this on the main page as well instead of 
creating a sub-menu.

<h2>Examples</h2>
Within the Hugo documentation we sometimes already provide examples of how to use a command, e.g. <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/econometrics/panel/" target="_blank">panel</a> 
adding one or two examples with more detail here helps explain how one can use some commands. E.g. using some command 
in the Stocks menu requires you to load a ticker before you can use it or requires an API Key (where you can refer back to the Getting Started guide) It can be helpful to guide the user 
through these steps. What commands you show is completely up to you.<br></br>

Make sure to include links to the relevant educational pages, e.g. if you mention 'moving average', use the following 
instead: "*The following command calculates the <a href="https://www.investopedia.com/terms/m/movingaverage.asp" target="_blank">moving average (MA)</a>.*"
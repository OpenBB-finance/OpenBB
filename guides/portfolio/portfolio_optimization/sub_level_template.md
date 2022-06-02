---
title: Introduction to ENTER_MENU_NAME_HERE
keywords: "ENTER_KEY_WORD_HERE, ENTER_KEY_WORD_HERE, ENTER_KEY_WORD_HERE, ENTER_KEY_WORD_HERE"
date: "YEAR-MONTH-DAY"
type: our story
status: publish
excerpt: "The Introduction to ENTER_MENU_NAME_HERE within the ENTER_TOP_LEVEL_MENU_NAME_HERE explains how to use the 
ENTER_MENU_NAME_HERE and provides a brief description of its sub-menus"
geekdocCollapseSection: true
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
  - Include a link tot the image as well, e.g: `<a target="_blank" href="https://user-images.githubusercontent.com/46355364/170244924-ffe6cd15-8d17-4690-bf44-d2b496dbc310.png"><img alt="headlines" src="https://user-images.githubusercontent.com/46355364/170244924-ffe6cd15-8d17-4690-bf44-d2b496dbc310.png"></a>`
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
The purpose of the menu, providing very factual information with a neutral view. E.g. "The options menu is used to 
gain insights in different metrics involved around option contracts based on the selected ticker."

<h2>How to use</h2>
Explain in detail how to use the menu. Sticking with the Options menu, you would want to understand how to <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/options/load/" target="_blank">load</a> a 
ticker, the fact you need to set an expiration date with <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/options/exp/" target="_blank">exp</a> and then how to use parameters, giving a few examples. <br></br>

Make sure that you link to the Hugo documentation for each command you mention here so people can view in more detail 
how the command works exactly. Make use of HTML here so the guides page on the website doesn't close down.

<h2>Sub-menus available</h2>
Provide a brief description of each menu available and include a link to that menu. E.g, the option menu could 
have the following:

- <a href="//" target="_blank">Introduction to Hedge</a>: provides the capabilities to determine how to delta, gamma and vega hedge a position.
- <a href="//" target="_blank">Introduction to Pricing</a>: shows options pricing and risk neutral valuation.

It could be that these menus are so small that it makes sense to include this on the main page as well instead of 
creating another sub-menu.

<h2>Examples</h2>
Within the Hugo documentation we sometimes already provide examples of how to use a command, e.g. <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/econometrics/panel/" target="_blank">panel</a> 
adding one or two examples with more detail here helps explain how one can use some commands. E.g. using some command 
in the Options menu requires you to load a ticker and set an expiration date. It can be helpful to guide the user 
through these steps. What commands you show is completely up to you. <br></br>

Make sure to include links to the relevant educational pages, e.g. if you mention 'Delta', use the following 
instead: "*The following command calculates the <a href="https://www.investopedia.com/terms/d/delta.asp" target="_blank">delta</a> of the option.*"
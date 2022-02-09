The Discord Bot can be added to a server by users with admin privileges through the link below: 

https://discord.com/oauth2/authorize?client_id=927232119346962513&permissions=510500797553&scope=bot%20applications.commands

<img width="1400" alt="Discord Bot on GST Discord Server" src="https://user-images.githubusercontent.com/85772166/153071762-9da3845d-da06-47af-a147-bea5488524a3.png">

Users can interact with the bot through both direct messages and the server. Alternatively, the bot can be run locally on a private server using the installation instructions found here: https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/discordbot#readme

The bot is called by using the slash key - / - in the server or in a direct message to the bot. To explore the commands, click on the bot's avatar.

<img width="1400" alt="Discord Bot Slash Command Example" src="https://user-images.githubusercontent.com/85772166/153072692-c3d458ef-1f5a-48c8-9173-6d35e0af5ad1.png">

/cmds will show a text list of commands along with the different options available for each.

<img width="1400" alt="Discord Bot Command List" src="https://user-images.githubusercontent.com/85772166/153074728-95b1dfff-10d8-43f7-a6a7-59f904975ada.png">

```
[ta-summary](ticker)
[ta-view](ticker)
[ta-recom](ticker)
[ta-obv](ticker) <START> <END>
[ta-fib](ticker) <START> <END>
[ta-ad](ticker) <OPEN> <START> <END>
[ta-cg](ticker) <LENGTH> <START> <END>
[ta-fisher](ticker) <LENGTH> <START> <END>
[ta-cci](ticker) <LENGTH> <SCALAR> <START> <END>
[ta-ema](ticker) <WINDOW> <OFFSET> <START> <END>
[ta-sma](ticker) <WINDOW> <OFFSET> <START> <END>
[ta-wma](ticker) <WINDOW> <OFFSET> <START> <END>
[ta-hma](ticker) <WINDOW> <OFFSET> <START> <END>
[ta-zlma](ticker) <WINDOW> <OFFSET> <START> <END>
[ta-aroon](ticker) <LENGTH> <SCALAR> <START> <END>
[ta-adosc](ticker) <OPEN> <FAST> <SLOW> <START> <END>
[ta-macd](ticker) <FAST> <SLOW> <SIGNAL> <START> <END>
[ta-kc](ticker) <LENGTH> <SCALAR> <MA_MODE> <START> <END>
[ta-adx](ticker) <LENGTH> <SCALAR> <DRIFT> <START> <END>
[ta-rsi](ticker) <LENGTH> <SCALAR> <DRIFT> <START> <END>
[ta-stoch](ticker) <FAST_K> <SLOW_D> <SLOW_K> <START> <END>
[ta-bbands](ticker) <LENGTH> <SCALAR> <MA_MODE> <START> <END>
[ta-donchian](ticker) <LWR_LENGTH> <UPR_LENGTH> <START> <END>

[opt-unu]()
[opt-iv](ticker)
[opt-vsurf](ticker) <z>
[opt-hist](ticker) <strike> <expiration> <opt-typ>
[opt-oi](ticker) <expiration> <min-sp> <max-sp>
[opt-vol](ticker) <expiration> <min-sp> <max-sp>
[opt-overview](ticker) <expiration> <min-sp> <max-sp>
[opt-chain](ticker) <expiration> <opt-typ> <min-sp> <max-sp>

[dps.hsi]() <NUM>
[dps.shorted](NUM)
[dps.psi](ticker)
[dps.spos](ticker)
[dps.dpotc](ticker)
[dps.pos]() <NUM> <SORT>
[dps.sidtc]() <NUM> <SORT>
[dps.ftd](ticker) <DATE_START> <DATE_END>

[dd-est](ticker)
[dd-sec](ticker)
[dd-analyst](ticker)
[dd-supplier](ticker)
[dd-customer](ticker)
[dd-arktrades](ticker)
[dd-pt](ticker) <RAW> <DATE_START>

[scr.presets_default]()
[scr.presets_custom]()
[scr.historical](SIGNAL) <START>
[scr.overview](PRESET) <SORT> <LIMIT> <ASCEND>
[scr.technical](PRESET) <SORT> <LIMIT> <ASCEND>
[scr.valuation](PRESET) <SORT> <LIMIT> <ASCEND>
[scr.financial](PRESET) <SORT> <LIMIT> <ASCEND>
[scr.ownership](PRESET) <SORT> <LIMIT> <ASCEND>
[scr.performance](PRESET) <SORT> <LIMIT> <ASCEND>

[gov-histcont](ticker)
[gov-lobbying](ticker) <NUM>
[gov-toplobbying]() <NUM> <RAW>
[gov-lastcontracts]() <DAYS> <NUM>
[gov-contracts](ticker) <DAYS> <RAW>
[gov-qtrcontracts]() <ANALYSIS> <NUM>
[gov-lasttrades]() <GOV_TYPE> <DAYS> <REP>
[gov-gtrades](ticker) <GOV_TYPE> <MONTHS> <RAW>
[gov-topbuys]() <GOV_TYPE> <MONTHS> <NUM> <RAW>
[gov-topsells]() <GOV_TYPE> <MONTHS> <NUM> <RAW>
<DAYS> = Past Transaction Days
<MONTHS> = Past Transaction Months

[econ-softs]()
[econ-meats]()
[econ-energy]()
[econ-metals]()
[econ-grains]()
[econ-futures]()
[econ-usbonds]()
[econ-glbonds]()
[econ-indices]()
[econ-overview]()
[econ-feargreed]()
[econ-currencies]()
[econ-valuation]() <GROUP>
[econ-performance]() <GROUP>

[disc-fidelity]()
[ins-last](ticker) <num>
[q](ticker)

```
<img width="1400" alt="Discord Bot Sample Output - /cc SPY" src="https://user-images.githubusercontent.com/85772166/153075094-42a608f4-04a9-4a83-9e41-3eb31f34ba30.png">

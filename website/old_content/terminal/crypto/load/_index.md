`usage: load [-c COIN] [-s START]
            [--exchange EXCHANGE]
            [-e END] [-i {1,5,15,30,60,240,1440,10080,43200}] [--vs VS] [--source {ccxt,yf,cg}] [-h]`

Load crypto currency to perform analysis on. Yahoo Finance is used as default source. Other sources can be used such as 'ccxt'
or 'cg' with --source. If you select 'ccxt', you can then select any exchange with --exchange. You can also select a specific
interval with --interval.

```
optional arguments:
  -c COIN, --coin COIN  Coin to get. Must be coin symbol (e.g., btc, eth) (default: None)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the crypto (default: 2019-08-19)
  --exchange {aax,ascendex,bequant,bibox,bigone,binance,binancecoinm,binanceus,binanceusdm,bit2c,bitbank,bitbay,bitcoincom,bitfinex,bitfinex2,bitflyer,bitforex,bitget,bithumb,bitmart,bitmex,bitopro,bitpanda,bitrue,bitso,bitstamp,bitstamp1,bittrex,bitvavo,bkex,bl3p,btcalpha,btcbox,btcex,btcmarkets,btctradeua,btcturk,buda,bw,bybit,bytetrade,cdax,cex,coinbaseprime,coinbasepro,coincheck,coinex,coinfalcon,coinmate,coinone,coinspot,crex24,cryptocom,currencycom,delta,deribit,digifinex,eqonex,exmo,flowbtc,fmfwio,ftx,ftxus,gate,gateio,gemini,hitbtc,hitbtc3,hollaex,huobi,huobijp,huobipro,idex,independentreserve,indodax,itbit,kraken,kucoin,kucoinfutures,kuna,latoken,lbank,lbank2,liquid,luno,lykke,mercado,mexc,mexc3,ndax,novadax,oceanex,okcoin,okex,okex5,okx,paymium,phemex,poloniex,probit,qtrade,ripio,stex,therock,tidebit,tidex,timex,tokocrypto,upbit,wavesexchange,whitebit,woo,xena,yobit,zaif,zb,zipmex,zonda}
                        Exchange to search (default: binance)
  -e END, --end END     The ending date (format YYYY-MM-DD) of the crypto (default: 2022-08-23)
  -i {1,5,15,30,60,240,1440,10080,43200}, --interval {1,5,15,30,60,240,1440,10080,43200}
                        The interval of the crypto (default: 1440)
  --vs VS               Quote currency (what to view coin vs). e.g., usdc, usdt, ... if source is ccxt, usd, eur, ... otherwise
                        (default: usdt)
  --source {ccxt,yf,cg}
                        Data source to select from (default: yf)
  -h, --help            show this help message (default: False)
```
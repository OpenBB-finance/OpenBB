```
usage: parity [-p] [-a] [-m MINIMUM] [-M MAXIMUM] [-h]
```

An advanced strategy that seeks arbitrage opportunites in put-call spreads relative to the forward underlying asset price; put-call parity defines the relationship between calls, puts and the underlying futures contract.

This principle requires that the puts and calls are the same strike, same expiration and have the same underlying futures contract.  The put call relationship is highly correlated, so if put call parity is violated, an arbitrage opportunity exists.

The formula for put call parity is c + k = f +p, meaning the call price plus the strike price of both options is equal to the futures price plus the put price.
```
c = call price
k = strike price
f = futures price
p = put price
```
<img size="1400" alt="put-call parity equation" src="https://user-images.githubusercontent.com/85772166/142464757-da18061f-5b18-4641-b908-f2d9d392edc6.jpeg">

For a detailed explanation, see: https://www.cmegroup.com/education/courses/introduction-to-options/put-call-parity.html
Examples of S&P futures can be seen here: https://www.cmegroup.com/markets/equities/sp/e-mini-sandp500.quotes.html

```
optional arguments:
  -a, --ask             uses ask price instead of lastPrice (default: False)
  -p, --put             shows puts instead of calls (default: False)
  -m, --min             the minimum strike price to be shown (default: None)
  -M, --max             the maximum strike price to be shown (default: None)
  -h, --help            show this help message (default: False)
```
<img size="1400" alt="Feature Screenshot - parity" src="https://user-images.githubusercontent.com/85772166/142463437-558b2335-1a19-4d81-8184-0721abd7abcb.png">


import urllib.request, json
url = 'http://localhost:6900/api/v1/quant_ml/macro/expression'
for k in ['FRED:INDPRO', 'FRED:PAYEMS', 'FRED:RSAFS', 'FRED:VIXCLS', 'SPY/IEF']:
    try:
        req = urllib.request.Request(url, data=json.dumps({'expr': k, 'transform': 'yoy_zscore'}).encode(), headers={'Content-Type': 'application/json'})
        res = json.loads(urllib.request.urlopen(req).read())
        d = res.get('data', [])
        print(f"{k} Count: {len(d)} Latest: {d[-1]['date'] if d else 'None'}")
    except Exception as e:
        print(k, e)

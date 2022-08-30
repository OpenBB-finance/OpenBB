```
usage: orders [-l LIMIT] [-s {product_id,side,price,size,type,created_at,status}] [--descend] [--export {csv,json,xlsx}] [-h]
```
List your current open orders
```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Limit parameter. (default: 20)
  -s {product_id,side,price,size,type,created_at,status}, --sort {product_id,side,price,size,type,created_at,status}
                        Sort by given column. Default: created_at (default: created_at)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

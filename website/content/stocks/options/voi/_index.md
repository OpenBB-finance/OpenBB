```
usage: voi [-v MIN_VOL] [-m MIN_SP] [-M MAX_SP] [-s {tr,yf}] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Plots volume and open interest of calls vs puts for the selected expiration date.

```
optional arguments:
  -v MIN_VOL, --minv MIN_VOL
                        minimum volume (considering open interest) threshold of the plot. (default: -1)
  -m MIN_SP, --min MIN_SP
                        minimum strike price to consider in the plot. (default: -1)
  -M MAX_SP, --max MAX_SP
                        maximum strike price to consider in the plot. (default: -1)
  -s {tr,yf}, --source {tr,yf}
                        Source to get data from (default: tr)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

![voi](https://user-images.githubusercontent.com/46355364/154290408-ae5d50ff-74ea-4705-b8ea-e4eebc842bb6.png)

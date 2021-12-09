```
usage: performance
                   [-g {sector,industry,basic materials,communication services,consumer cyclical,consumer defensive,energy,financial,healthcare,industrials,real Estate,technology,utilities,country,capitalization}]
                   [-s {Name,Week,Month,3Month,6Month,1Year,YTD,Recom,AvgVolume,RelVolume,Change,Volume}] [-a] [--export {csv,json,xlsx}] [-h]
```

View group (sectors, industry or country) performance data. https://finviz.com

```
optional arguments:
  -g {sector,industry,basic materials,communication services,consumer cyclical,consumer defensive,energy,financial,healthcare,industrials,real Estate,technology,utilities,country,capitalization}, --group {sector,industry,basic materials,communication services,consumer cyclical,consumer defensive,energy,financial,healthcare,industrials,real Estate,technology,utilities,country,capitalization}
                        Data group (sector, industry or country) (default: Sector)
  -s {Name,Week,Month,3Month,6Month,1Year,YTD,Recom,AvgVolume,RelVolume,Change,Volume}, --sortby {Name,Week,Month,3Month,6Month,1Year,YTD,Recom,AvgVolume,RelVolume,Change,Volume}
                        Column to sort by (default: Name)
  -a, -ascend           Flag to sort in ascending order (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
<img size="1400" alt="Feature Screenshot - performance" src="https://user-images.githubusercontent.com/85772166/141923981-609641aa-cac2-4677-b356-3fbba9a2e4c9.png">

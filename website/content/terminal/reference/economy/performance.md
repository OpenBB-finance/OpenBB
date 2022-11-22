---
title: performance
description: OpenBB Terminal Function
---

# performance

View group (sectors, industry or country) performance data. [Source: Finviz]

### Usage

```python
usage: performance [-g {sector,industry,basic_materials,communication_services,consumer_cyclical,consumer_defensive,energy,financial,healthcare,industrials,real_Estate,technology,utilities,country,capitalization}]
                   [-s {Name,Week,Month,3Month,6Month,1Year,YTD,Recom,AvgVolume,RelVolume,Change,Volume}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| group | Data group (sector, industry or country) | sector | True | sector, industry, basic_materials, communication_services, consumer_cyclical, consumer_defensive, energy, financial, healthcare, industrials, real_Estate, technology, utilities, country, capitalization |
| sortby | Column to sort by | Name | True | Name, Week, Month, 3Month, 6Month, 1Year, YTD, Recom, AvgVolume, RelVolume, Change, Volume |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
---


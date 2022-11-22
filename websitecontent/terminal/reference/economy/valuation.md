---
title: valuation
description: OpenBB Terminal Function
---

# valuation

View group (sectors, industry or country) valuation data. [Source: Finviz]

### Usage

```python
usage: valuation [-g {sector,industry,basic_materials,communication_services,consumer_cyclical,consumer_defensive,energy,financial,healthcare,industrials,real_Estate,technology,utilities,country,capitalization}]
                 [-s {Name,MarketCap,P/E,FwdP/E,PEG,P/S,P/B,P/C,P/FCF,EPSpast5Y,EPSnext5Y,Salespast5Y,Change,Volume}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| group | Data group (sectors, industry or country) | sector | True | sector, industry, basic_materials, communication_services, consumer_cyclical, consumer_defensive, energy, financial, healthcare, industrials, real_Estate, technology, utilities, country, capitalization |
| sortby | Column to sort by | Name | True | Name, MarketCap, P/E, FwdP/E, PEG, P/S, P/B, P/C, P/FCF, EPSpast5Y, EPSnext5Y, Salespast5Y, Change, Volume |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
---


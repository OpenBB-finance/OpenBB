---
title: ycrv
description: This documentation page explains how the user is able to use ycrv command to generate country yield curve, which shows the bond rates at different maturities.
keywords:
- bond rates
- yield curve
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /ycrv - Reference | OpenBB Terminal Docs" />

Generate country yield curve. The yield curve shows the bond rates at different maturities.

### Usage

```python
ycrv [-c {argentina,australia,austria,bahrain,bangladesh,belgium,botswana,brazil,bulgaria,canada,chile,china,colombia,croatia,cyprus,czech republic,denmark,egypt,finland,france,germany,greece,hong kong,hungary,iceland,india,indonesia,ireland,israel,italy,japan,jordan,kenya,latvia,lithuania,luxembourg,malaysia,malta,mauritius,mexico,morocco,namibia,netherlands,new zealand,nigeria,norway,pakistan,peru,philippines,poland,portugal,qatar,romania,russia,saudi arabia,serbia,singapore,slovakia,slovenia,south africa,south korea,spain,sri lanka,sweden,switzerland,taiwan,thailand,turkey,uganda,ukraine,united kingdom,united states,venezuela,vietnam}] [-d DATE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| country | Yield curve for a country. Ex: united_states | united_states | True | argentina, australia, austria, bahrain, bangladesh, belgium, botswana, brazil, bulgaria, canada, chile, china, colombia, croatia, cyprus, czech republic, denmark, egypt, finland, france, germany, greece, hong kong, hungary, iceland, india, indonesia, ireland, israel, italy, japan, jordan, kenya, latvia, lithuania, luxembourg, malaysia, malta, mauritius, mexico, morocco, namibia, netherlands, new zealand, nigeria, norway, pakistan, peru, philippines, poland, portugal, qatar, romania, russia, saudi arabia, serbia, singapore, slovakia, slovenia, south africa, south korea, spain, sri lanka, sweden, switzerland, taiwan, thailand, turkey, uganda, ukraine, united kingdom, united states, venezuela, vietnam |
| date | Date to get data from FRED. If not supplied, the most recent entry will be used. | None | True | None |

---

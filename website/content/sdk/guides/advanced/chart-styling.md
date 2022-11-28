---
title: Adjusting Chart Style
sidebar_position: 4
---

Within the OpenBB SDK, you can customize your chart style. You can switch between `dark` and `light` easily using this block of code:

```python
from openbb_terminal.sdk import TerminalStyle
theme = TerminalStyle("light", "light", "light")
```

![Light Mode](https://user-images.githubusercontent.com/40023817/193700307-cbb12edc-0a5d-4804-9f3c-a798efd9e69d.png)

OR

```python
from openbb_terminal.sdk import TerminalStyle
theme = TerminalStyle("dark", "dark", "dark")
```

![Dark Mode](https://user-images.githubusercontent.com/40023817/193699221-e154995b-653c-40fd-8fc6-a3f8d39638db.png)

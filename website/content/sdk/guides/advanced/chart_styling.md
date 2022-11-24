---
title: Adjusting Chart Style
sidebar_position: 2
---

With OpenBB SDK, you can customize your chart style. You can switch between `dark` and `light` easily using this block of code:

```python
from openbb_terminal.sdk import TerminalStyle
theme = TerminalStyle("light", "light", "light")
```

<img width="813" alt="Screenshot 2022-10-03 at 23 56 52" src="https://user-images.githubusercontent.com/40023817/193700307-cbb12edc-0a5d-4804-9f3c-a798efd9e69d.png">

OR

```python
from openbb_terminal.sdk import TerminalStyle
theme = TerminalStyle("dark", "dark", "dark")
```

<img width="791" alt="Screenshot 2022-10-03 at 23 46 33" src="https://user-images.githubusercontent.com/40023817/193699221-e154995b-653c-40fd-8fc6-a3f8d39638db.png">
---
title: KaTeX
---

[KaTeX](https://katex.org/) shortcode let you render math typesetting in markdown document.

## Example

{{< columns >}}

```latex
{{</* katex [display] [class="text-center"] */>}}
f(x) = \int_{-\infty}^\infty\hat f(\xi)\,e^{2 \pi i \xi x}\,d\xi
{{</* /katex */>}}
```

<--->

<!-- spellchecker-disable -->
<!-- prettier-ignore -->
{{< katex display >}}
f(x) = \int_{-\infty}^\infty\hat f(\xi)\,e^{2 \pi i \xi x}\,d\xi
{{< /katex >}}

<!-- spellchecker-enable -->

{{< /columns >}}

KaTeX can also be used inline, for example {{< katex >}}\pi(x){{< /katex >}} or used with a `display` setting. for example `display: block`:

<!-- spellchecker-disable -->
<!-- prettier-ignore -->
{{< katex display >}}
f(x) = \int_{-\infty}^\infty\hat f(\xi)\,e^{2 \pi i \xi x}\,d\xi
{{< /katex >}}

<!-- spellchecker-enable -->

Text continues here.

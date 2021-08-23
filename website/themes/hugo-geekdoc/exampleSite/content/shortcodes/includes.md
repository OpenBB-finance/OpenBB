---
title: Includes
---

{{< toc >}}

Include shortcode can include files of different types. By specifying a language, the included file will have syntax highlighting.

```tpl
{{</* include file="relative/path/from/hugo/root" language="go" markdown=[false|true] */>}}
```

Attributes:

| Name     | Usage                                                                                                                               | default         |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| file     | path to the included file relative to the Hugo root                                                                                 | undefined       |
| language | language for [syntax highlighting](https://gohugo.io/content-management/syntax-highlighting/#list-of-chroma-highlighting-languages) | undefined       |
| type     | special include type (`html,page`)                                                                                                  | undefined       |
| options  | highlighting [options](https://gohugo.io/content-management/syntax-highlighting/#highlight-shortcode)                               | `linenos=table` |

## Examples

### Markdown file (default)

If no other options are specified, files will be rendered as Markdown using the `RenderString` [function](https://gohugo.io/functions/renderstring/).

{{< hint warning >}}
**Location of markdown files**\
If you include markdown files that should not get a menu entry, place them outside the content folder or exclude them otherwise.
{{< /hint >}}

```tpl
{{</* include file="/static/_includes/example.md.part" */>}}
```

<!-- prettier-ignore-start -->
<!-- spellchecker-disable -->
{{< include file="/static/_includes/example.md.part" >}}
<!-- spellchecker-enable -->
<!-- prettier-ignore-end -->

### Language files

This method can be used to include source code files and keep them automatically up to date.

```tpl
{{</* include file="config.yaml" language="yaml" options="linenos=table,hl_lines=5-6,linenostart=100" */>}}
```

<!-- prettier-ignore-start -->
<!-- spellchecker-disable -->
{{< include file="config.yaml" language="yaml" options="linenos=table,hl_lines=5-6,linenostart=100">}}
<!-- spellchecker-enable -->
<!-- prettier-ignore-end -->

### Special include types

#### HTML

HTML content will be filtered by the `safeHTML` filter and added to the rendered page output.

```tpl
{{</* include file="/static/_includes/example.html.part" */>}}
```

{{< include file="/static/_includes/example.html.part" type="html" >}}

#### Pages

In some situations, it can be helpful to include Markdown files that also contain shortcodes. While the [default method](#markdown-file-default) works fine to render plain Markdown, shortcodes are not parsed. The only way to get this to work is to use Hugo pages. There are several ways to structure these include pages, so whatever you do, keep in mind that Hugo needs to be able to render and serve these files as regular pages! How it works:

1. First you need to create a directory **within** your content directory. For this example site `_includes` is used.
2. To prevent the theme from embedding the page in the navigation, create a file `_includes/_index.md` and add `GeekdocHidden: true` to the front matter.
3. Place your Markdown files within the `_includes` folder e.g. `/_includes/include-page.md`. Make sure to name it `*.md`.
4. Include the page using `{{</* include file="/_includes/include-page.md" */>}}`.

Resulting structure should look like this:

```Shell
_includes/
 ├── include-page.md
 └── _index.md
```

{{< include file="/_includes/include-page.md" type="page" >}}

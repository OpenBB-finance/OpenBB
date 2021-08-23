There are multiple ways to add code blocks. Most of them works out of the box only the Hugo shortcode `<highlight>` need some configuration to work properly.

{{< toc >}}

## Inline code

To display an inline shortcode use single quotes:

```plain
`some code`
```

**Example:** `some code`

## Code blocks

Code blocks can be uses without language specification:

````markdown
```
some code
```
````

**Example:**

```plain
some code
```

... or if you need language specific syntax highlighting:

````markdown
```Shell
# some code
echo "Hello world"
```
````

**Example:**

```Shell
# some code
echo "Hello World"
```

## Highlight shortcode

Hugo has a build-in shortcode for syntax highlighting. To work properly with this theme, you have to set following options in your site configuration:

{{< tabs "uniqueid" >}}
{{< tab "TOML" >}}

```TOML
pygmentsUseClasses=true
pygmentsCodeFences=true
```

{{< /tab >}}
{{< tab "YAML" >}}

```YAML
pygmentsUseClasses: true
pygmentsCodeFences: true
```

{{< /tab >}}
{{< /tabs >}}

You can use it like every other shortcode:

<!-- prettier-ignore -->
```markdown
{{</* highlight Shell "linenos=table" */>}}
# some code
echo "Hello World"
{{</* /highlight */>}}
```

**Example:**

<!-- markdownlint-disable -->

<!-- prettier-ignore-start -->
{{< highlight Shell "linenos=table" >}}
# some code
echo "Hello World"
{{< /highlight >}}
<!-- prettier-ignore-end-->

<!-- markdownlint-enable -->

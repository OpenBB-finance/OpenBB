---
title: Getting Started
weight: -20
---

This page tells you how to get started with the Geekdoc theme, including installation and basic configuration.

<!--more-->

{{< toc >}}

## Install requirements

You need a recent version of Hugo for local builds and previews of sites that use Geekdoc. As we are using [gulp](https://gulpjs.com/) as pre-processor the normal version of Hugo is sufficient. If you prefer the extended version of Hugo anyway this will work as well. For comprehensive Hugo documentation, see [gohugo.io](https://gohugo.io/documentation/).

If you want to use the theme from a cloned branch instead of a release tarball you'll need to install `gulp` locally and run the default pipeline once to create all required assets.

```Shell
# install required packages from package.json
npm install

# run gulp pipeline to build required assets
npx gulp default
```

## Using the theme

To prepare your new site environment just a few steps are required:

1. Create a new empty Hugo site.

   ```Shell
   hugo new site demosite
   ```

2. Switch to the root of the new site.

   ```Shell
   cd demosite
   ```

3. Install the Geekdoc theme from a [release bundle](#option-1-download-pre-build-release-bundle) (recommended) or from [Git branch](#option-2-clone-the-github-repository).

4. Create the minimal required Hugo configuration `config.toml`. For all configuration options take a look at the [configuration](/usage/configuration/) page.

   ```Toml
   baseURL = "http://localhost"
   title = "Geekdocs"
   theme = "hugo-geekdoc"

   pluralizeListTitles = false

   # Geekdoc required configuration
   pygmentsUseClasses = true
   pygmentsCodeFences = true
   disablePathToLower = true

   # Needed for mermaid shortcodes
   [markup]
     [markup.goldmark.renderer]
       # Needed for mermaid shortcode
       unsafe = true
     [markup.tableOfContents]
       startLevel = 1
       endLevel = 9
   ```

5. Test your site.

   ```Shell
   hugo server -D
   ```

### Option 1: Download pre-build release bundle

Download and extract the latest release bundle into the theme directory.

```Shell
mkdir -p themes/hugo-geekdoc/
curl -L https://github.com/thegeeklab/hugo-geekdoc/releases/latest/download/hugo-geekdoc.tar.gz | tar -xz -C themes/hugo-geekdoc/ --strip-components=1
```

### Option 2: Clone the GitHub repository

{{< hint info >}}
**Info**\
Keep in mind this method is not recommended and needs some extra steps to get it working.
If you want to use the Theme as submodule keep in mind that your build process need to
run the described steps as well.
{{< /hint >}}

Clone the Geekdoc git repository.

```Shell
git clone https://github.com/thegeeklab/hugo-geekdoc.git themes/geekdoc
```

Build required theme assets e.g. CSS files and SVG sprites with `gulp`.

```Shell
npx gulp default
```

## Deployments

### Netlify

There are several ways to deploy your site with this theme on Netlify. Regardless of which solution you choose, the main goal is to ensure that the prebuilt theme release tarball is used or to run the [required commands](#option-2-clone-the-github-repository) to prepare the theme assets before running the Hugo build command.

Here are some possible solutions:

**Use a Makefile:**

Add a Makefile to your repository to bundle the required steps.

```Makefile
THEME_VERSION := v0.8.2
THEME := hugo-geekdoc
BASEDIR := docs
THEMEDIR := $(BASEDIR)/themes

.PHONY: doc
doc: doc-assets doc-build

.PHONY: doc-assets
doc-assets:
   mkdir -p $(THEMEDIR)/$(THEME)/ ; \
   curl -sSL "https://github.com/thegeeklab/$(THEME)/releases/download/${THEME_VERSION}/$(THEME).tar.gz" | tar -xz -C $(THEMEDIR)/$(THEME)/ --strip-components=1

.PHONY: doc-build
doc-build:
        cd $(BASEDIR); hugo

.PHONY: clean
clean:
   rm -rf $(THEMEDIR) && \
   rm -rf $(BASEDIR)/public
```

This Makefile can be used in your `netlify.toml`, take a look at the Netlify [example](https://docs.netlify.com/configure-builds/file-based-configuration/#sample-file) for more information:

```toml
[build]
publish = "docs/public"
command = "make doc"
```

**Chain required commands:**

Chain all required commands to prepare the theme and build your site on the `command` option in your `netlify.toml` like this:

```toml
[build]
publish = "docs/public"
command = "command1 && command 2 && command3 && hugo"
```

### Subdirectories

{{< hint danger >}}
**Warning**\
As deploying Hugo sites on subdirectories is not as robust as on subdomains, we do not recommend this.
If you have a choice, using a domain/subdomain should always be the preferred solution!
{{< /hint >}}

If you want to deploy your side to a subdirectory of your domain, some extra steps are required:

- Configure your Hugo base URL e.g. `baseURL = http://localhost/demo/`.
- Don't use `relativeURLs: false` nor `canonifyURLs: true` as is can cause unwanted side effects!

There are two ways to get Markdown links or images working:

- Use the absolute path including your subdirectory e.g. `[testlink](/demo/example-site)`
- Overwrite the HTML base in your site configuration with `geekdocOverwriteHTMLBase = true` and use the relative path e.g. `[testlink](example-site)`

But there is another special case if you use `geekdocOverwriteHTMLBase = true`. If you use anchors in your Markdown links you have to ensure to always include the page path. As an example `[testlink](#some-anchor)` will resolve to `http://localhost/demo/#some-anchor` and not automatically include the current page!

## Known Limitations

### Minify HTML results in spacing issues

Using `hugo --minify` without further configuration or using other minify tools that also minify HTML files might result in spacing issues in the theme and is **not** supported.

After some testing we decided to not spend effort to fix this issue for now as the benefit is very low. There are some parts of the theme where spaces between HTML elements matters but were stripped by minify tools. Some of these issues are related to <!-- spellchecker-disable -->[gohugoio/hugo#6892](https://github.com/gohugoio/hugo/issues/6892).<!-- spellchecker-enable --> While recommendation like "don't depend on whitespace in your layout" sounds reasonable, it seems to be not that straight forward especially for something like embedded icons into the text flow.

If you still want to use Hugo's minify flag you should at least exclude HTML file in your site [configuration](https://gohugo.io/getting-started/configuration/#configure-minify):

```toml
[minify]
  disableHTML = true
```

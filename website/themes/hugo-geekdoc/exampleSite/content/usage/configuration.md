---
title: Configuration
weight: -10
---

{{< toc >}}

## Site configuration

{{< tabs "site-config" >}}
{{< tab "TOML" >}}

```Toml
baseURL = "http://localhost"
title = "Geekdocs"
theme = "hugo-geekdoc"

# Required to get well formatted code blocks
pygmentsUseClasses = true
pygmentsCodeFences = true
disablePathToLower = true
enableGitInfo = true

[markup]
  [markup.goldmark.renderer]
    # Needed for mermaid shortcode
    unsafe = true
  [markup.tableOfContents]
    startLevel = 1
    endLevel = 9

[params]
  # (Optional, default 6) Set how many table of contents levels to be showed on page.
  # Use false to hide ToC, note that 0 will default to 6 (https://gohugo.io/functions/default/)
  # You can also specify this parameter per page in front matter.
  geekdocToC = 3

  # (Optional, default static/brand.svg) Set the path to a logo for the Geekdoc
  # relative to your 'static/' folder.
  geekdocLogo = "logo.png"

  # (Optional, default false) Render menu from data file im 'data/menu/main.yaml'.
  geekdocMenuBundle = true

  # (Optional, default true) Show page navigation links at the bottom of each
  # docs page (bundle menu only).
  geekdocNextPrev = false

  # (Optional, default true) Show a breadcrumb navigation bar at the top of each docs page.
  # You can also specify this parameter per page in front matter.
  geekdocBreadcrumb = false

  # (Optional, default none) Set source repository location. Used for 'Edit this page' links.
  # You can also specify this parameter per page in front matter.
  geekdocRepo = "https://github.com/thegeeklab/hugo"

  # (Optional, default none) Enable 'Edit this page' links. Requires 'GeekdocRepo' param
  # and path must point to 'content' directory of repo.
  # You can also specify this parameter per page in front matter.
  geekdocEditPath = "edit/main/exampleSite/content"

  # (Optional, default true) Enables search function with flexsearch.
  # Index is built on the fly and might slowdown your website.
  geekdocSearch = false

  # (Optional, default false) Display search results with the parent folder as prefix. This
  # option allows you to distinguish between files with the same name in different folders.
  # NOTE: This parameter only applies when 'geekdocSearch = true'.
  geekdocSearchShowParent = true

  # (Optional, default none) Add a link to your Legal Notice page to the site footer.
  # It can be either a remote url or a local file path relative to your content directory.
  geekdocLegalNotice = "https://blog.example.com/legal"

  # (Optional, default none) Add a link to your Privacy Policy page to the site footer.
  # It can be either a remote url or a local file path relative to your content directory.
  geekdocPrivacyPolicy = "/privacy"

  # (Optional, default true) Add an anchor link to headlines.
  geekdocAnchor = true

  # (Optional, default true) Copy anchor url to clipboard on click.
  geekdocAnchorCopy = true

  # (Optional, default true) Enable or disable image lazy loading for images rendered
  # by the 'img' shortcode.
  geekdocImageLazyLoading = true

  # (Optional, default false) Set HTMl <base> to .Site.BaseURL if enabled. It might be required
  # if a subdirectory is used within Hugos BaseURL.
  # See https://developer.mozilla.org/de/docs/Web/HTML/Element/base.
  geekdocOverwriteHTMLBase = false

  # (Optional, default false) Auto-decrease brightness of images and add a slightly grayscale to avoid
  # bright spots while using the dark mode.
  geekdocDarkModeDim = false

  # (Optional, default true) Display a "Back to top" link in the site footer.
  geekdocBackToTop = true
```

{{< /tab >}}
{{< tab "YAML" >}}

```Yaml
---
baseURL: "http://localhost"
title: "Geekdocs"
theme: "hugo-geekdoc"

# Required to get well formatted code blocks
pygmentsUseClasses: true
pygmentsCodeFences: true
disablePathToLower: true
enableGitInfo: true

markup:
  goldmark:
    # Needed for mermaid shortcode
    renderer:
      unsafe: true
  tableOfContents:
    startLevel: 1
    endLevel: 9

params:
  # (Optional, default 6) Set how many table of contents levels to be showed on page.
  # Use false to hide ToC, note that 0 will default to 6 (https://gohugo.io/functions/default/)
  # You can also specify this parameter per page in front matter.
  geekdocToC: 3

  # (Optional, default static/brand.svg) Set the path to a logo for the Geekdoc
  # relative to your 'static/' folder.
  geekdocLogo: logo.png

  # (Optional, default false) Render menu from data file im 'data/menu/main.yaml'.
  # See also https://geekdocs.de/usage/menus/#bundle-menu
  geekdocMenuBundle: true

  # (Optional, default false) Collapse all menu entries, can not be overwritten
  # per page if enabled. Can be enabled per page via `geekdocCollapseSection`
  geekdocCollapseAllSections: true

  # (Optional, default true) Show page navigation links at the bottom of each
  # docs page (bundle menu only).
  geekdocNextPrev: false

  # (Optional, default true) Show a breadcrumb navigation bar at the top of each docs page.
  # You can also specify this parameter per page in front matter.
  geekdocBreadcrumb: false

  # (Optional, default none) Set source repository location. Used for 'Edit this page' links.
  # You can also specify this parameter per page in front matter.
  geekdocRepo: "https://github.com/thegeeklab/hugo-geekdoc"

  # (Optional, default none) Enable "Edit this page" links. Requires 'GeekdocRepo' param
  # and path must point to 'content' directory of repo.
  # You can also specify this parameter per page in front matter.
  geekdocEditPath: edit/main/exampleSite/content

  # (Optional, default true) Enables search function with flexsearch.
  # Index is built on the fly and might slowdown your website.
  geekdocSearch: false

  # (Optional, default false) Display search results with the parent folder as prefix. This
  # option allows you to distinguish between files with the same name in different folders.
  # NOTE: This parameter only applies when 'geekdocSearch: true'.
  geekdocSearchShowParent: true

  # (Optional, default none) Add a link to your Legal Notice page to the site footer.
  # It can be either a remote url or a local file path relative to your content directory.
  geekdocLegalNotice: "https://blog.example.com/legal"

  # (Optional, default none) Add a link to your Privacy Policy page to the site footer.
  # It can be either a remote url or a local file path relative to your content directory.
  geekdocPrivacyPolicy: "/privacy"

  # (Optional, default true) Add an anchor link to headlines.
  geekdocAnchor: true

  # (Optional, default true) Copy anchor url to clipboard on click.
  geekdocAnchorCopy: true

  # (Optional, default true) Enable or disable image lazy loading for images rendered
  # by the 'img' shortcode.
  geekdocImageLazyLoading: true

  # (Optional, default false) Set HTMl <base> to .Site.BaseURL if enabled. It might be required
  # if a subdirectory is used within Hugos BaseURL.
  # See https://developer.mozilla.org/de/docs/Web/HTML/Element/base.
  geekdocOverwriteHTMLBase: false

  # (Optional, default false) Auto-decrease brightness of images and add a slightly grayscale to avoid
  # bright spots while using the dark mode.
  geekdocDarkModeDim: false

  # (Optional, default true) Display a "Back to top" link in the site footer.
  geekdocBackToTop: true
```

{{< /tab >}}
{{< /tabs >}}

## Page configuration

{{< tabs "page-config" >}}
{{< tab "TOML" >}}

```Toml
# Set type to 'posts' if you want to render page as blogpost
type = "posts"

# Set page weight to re-arrange items in file-tree menu.
weight = 10

# Set how many table of contents levels to be showed on page.
geekdocToC = 3

# Set a description for the current page. This will be shown in toc-trees objects.
geekdocDescription =

# Set false to hide the whole left navigation sidebar. Beware that it will make
# navigation pretty hard without adding some kind of on-page navigation.
geekdocNav = true

# Show a breadcrumb navigation bar at the top of each docs page.
geekdocBreadcrumb = false

# Set source repository location.
geekdocRepo = "https://github.com/thegeeklab/hugo-geekdoc"

# Enable "Edit this page" links. Requires 'GeekdocRepo' param and path must point
# to 'content' directory of repo.
geekdocEditPath = "edit/main/exampleSite/content"

# Used for 'Edit this page' link, set to '.File.Path' by default.
# Can be overwritten by a path relative to 'geekdocEditPath'
geekdocFilePath =

# Set to mark page as flat section (file-tree menu only).
geekdocFlatSection = true

# Set true to hide page or section from side menu (file-tree menu only).
geekdocHidden = true

# Set false to show this page as a file-tree menu entry when you want it to be hidden in the sidebar.
# NOTE: Only applies when 'geekdocHidden = true'.
geekdocHiddenTocTree = true

# Set to true to make a section foldable in side menu.
geekdocCollapseSection = true

# Add an anchor link to headlines.
geekdocAnchor = true

# If you have protected some pages with e.g. basic authentication you may want to exclude these pages
# from data file, otherwise information may be leaked. Setting this parameter to 'true' will exclude the
# page from search data, feeds, etc.
# WARNING: Consider hosting a standalone, fully auth-protected static page for secret information instead!
geekdocProtected = false

# Set 'left' (default), 'center' or 'right' to configure the text align of a page.
geekdocAlign = "left"
```

{{< /tab >}}
{{< tab "YAML" >}}

```Yaml
# Set type to 'posts' if you want to render page as blogpost.
type: "posts"

# Set page weight to re-arrange items in file-tree menu.
weight: 10

# Set how many table of contents levels to be showed on page.
geekdocToC: 3

# Set a description for the current page. This will be shown in toc-trees objects.
geekdocDescription:

# Set false to hide the whole left navigation sidebar. Beware that it will make
# navigation pretty hard without adding some kind of on-page navigation.
geekdocNav: true

# Show a breadcrumb navigation bar at the top of each docs page.
geekdocBreadcrumb: false

# Set source repository location.
geekdocRepo: "https://github.com/thegeeklab/hugo-geekdoc"

# Enable "Edit this page" links. Requires 'GeekdocRepo' param and path must point
# to 'content' directory of repo.
geekdocEditPath: "edit/main/exampleSite/content"

# Used for 'Edit this page' link, set to '.File.Path' by default.
# Can be overwritten by a path relative to 'geekdocEditPath'
geekdocFilePath:

# Set to mark page as flat section (file-tree menu only).
geekdocFlatSection: true

# Set true to hide page or section from side menu (file-tree menu only).
geekdocHidden: true

# Set false to show this page as a file-tree menu entry when you want it to be hidden in the sidebar.
# NOTE: Only applies when 'geekdocHidden: true'.
geekdocHiddenTocTree: true

# Set to true to make a section foldable in side menu.
geekdocCollapseSection: true

# Add an anchor link to headlines.
geekdocAnchor: true

# If you have protected some pages with e.g. basic authentication you may want to exclude these pages
# from data file, otherwise information may be leaked. Setting this parameter to 'true' will exclude the
# page from search data, feeds, etc.
# WARNING: Consider hosting a standalone, fully auth-protected static page for secret information instead!
geekdocProtected: false

# Set 'left' (default), 'center' or 'right' to configure the text align of a page.
geekdocAlign: "left"
```

{{< /tab >}}
{{< /tabs >}}

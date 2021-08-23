The theme supports two different kinds of menus. File-tree menu is the default one and does not require further configuration to work. If you want full control about your menu the bundle menu is a powerful option to accomplish it.

{{< toc >}}

## File-tree menu

As the name already suggests, the file tree menu builds a menu from the file system structure of the content folder. By default, areas and subareas are sorted alphabetically by the title of the pages. To manipulate the order the `weight` parameter in a page [front matter](https://gohugo.io/content-management/front-matter/) can be used. To structure your content folder you have to use [page bundles](https://gohugo.io/content-management/organization/#page-bundles), single files are **not** supported. Hugo will render build single files in the content folder just fine but it will not be added to the menu.

**Example:**

File system structure:

```plain
content/
├── level-1
│   ├── _index.md
│   ├── level-1-1.md
│   ├── level-1-2.md
│   └── level-1-3
│       ├── _index.md
│       └── level-1-3-1.md
└── level-2
    ├── _index.md
    ├── level-2-1.md
    └── level-2-2.md
```

[![Example file-tree menu](/media/file-tree.png)](/media/file-tree.png)

## Bundle menu

This type of navigation needs to be enabled first by setting `geekdocMenuBundle` to `true` in your [site configuration](/usage/configuration/#site-configuration). After you have activated the bundle menu, you start with an empty navigation. This is intentional because bundle menus have to be defined manually in a data file. While this increases the effort it also offers maximum flexibility in the design. The data file needs to be written in YAML and placed at `data/menu/main.yml`.

**Example:**

```YAML
---
main:
  - name: Level 1
    ref: "/level-1"
    icon: "gdoc_notification"
    sub:
      - name: Level 1.1
        ref: "/level-1/level-1-1"
      - name: Level 1.2
        ref: "/level-1/level-1-2"
      - name: Level 1.3
        ref: "/level-1/level-1-3"
        sub:
          - name: Level 1.3.1
            ref: "/level-1/level-1-3/level-1-3-1"
  - name: Level 2
    ref: "/level-2"
    sub:
      - name: Level 2.1
        ref: "/level-2/level-2-1"
      - name: Level 2.2
        ref: "/level-2/level-2-2"
```

As an advantage you can add [icons](/features/icon-sets/) to your menu entries e.g. `icon: "gdoc_notification"`.

[![Example bundle menu](/media/bundle-menu.png)](/media/bundle-menu.png)

### More menu

{{< hint ok >}}
**Tip**\
The more menu is special type of the bundle menu and can be combined with the default file-tree menu.
{{< /hint >}}

As this is a special type of the bundle menu it is basically working in the same way. To enable it just add a data file to `data/menu/more.yml`. The more menu will also work with the file-tree menu and therefor **don't need to be enabled** by the `geekdocMenuBundle` parameter.

**Example:**

```YAML
---
more:
  - name: News
    ref: "/#"
    icon: "gdoc_notification"
  - name: Releases
    ref: "https://github.com/thegeeklab/hugo-geekdoc/releases"
    external: true
    icon: "gdoc_download"
  - name: "View Source"
    ref: "https://github.com/thegeeklab/hugo-geekdoc"
    external: true
    icon: "gdoc_github"
```

[![Example bundle menu](/media/more-menu.png)](/media/more-menu.png)

## Extra Header Menu

If you want to customize the header menu, this can be achieved by using a data file written in YAML and placed at `data/menu/extra.yml`.

**Example:**

```Yaml
---
header:
  - name: GitHub
    ref: https://github.com/thegeeklab/hugo-geekdoc
    icon: gdoc_github
    external: true
```

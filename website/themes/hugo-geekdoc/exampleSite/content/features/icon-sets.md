---
title: Icon Sets
---

{{< toc >}}

## Custom icon sets

The only supported source for custom icons are SVG sprites. Some icon frameworks provides ready to use sprites e.g. FontAwesome. If the framework don't provide sprites, you can create your own from raw SVG icons. There are a lot of tools available to create sprites, please choose one that fits your need. One solution could be [svgsprit.es](https://svgsprit.es/).

Regardless of which tool (or existing sprite) you choose, there are a few requirements that must be met:

1. The sprite must be a valid **SVG** file.
2. You have to ensure to **hide the sprite**. Apply the predefined class `svg-sprite` or `hidden` to the root element of your sprite or add a small piece of inline CSS e.g. `style="display: none;"`.
3. Save the sprite to the folder `assets/sprites` right beside your `content` folder.

The result of a valid minimal SVG sprite file could look like this:

```XML
<svg class="svg-sprite" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <symbol viewBox="-2.29 -2.29 28.57 28.57" id="arrow_back" xmlns="http://www.w3.org/2000/svg">
        <path d="M24 10.526v2.947H5.755l8.351 8.421-2.105 2.105-12-12 12-12 2.105 2.105-8.351 8.421H24z"/>
    </symbol>
</svg>
```

**Example:**

FontAwesome provides three pre-build sprites included in the regular Web download pack, `sprites/brands.svg`, `sprites/regular.svg` and `sprites/solid.svg`. Choose your sprite to use and copy it to your projects root directory into `assets/sprites`, right beside your `content` folder:

```Bash
my_projcet/
├── assets
│   └── sprites
│       └── regular.svg
├── config.yaml
├── content
│   ├── _index.md
│   ├── ...
```

That's it! The theme will auto-load all available SVG sprites provided in the assets folder. To use the icons e.g. in the [bundle menu](/usage/menus/#bundle-menu), you need to lookup the id of the icon. An example would be `thumbs-up` {{< icon "thumbs-up" >}}. There is also a [shortcode](/shortcodes/icons/) available.

## Build-in icons

The theme bundles just a small set of hand crafted icons.

{{< sprites >}}

# Geekdoc

[![Build Status](https://img.shields.io/drone/build/thegeeklab/hugo-geekdoc?logo=drone&server=https%3A%2F%2Fdrone.thegeeklab.de)](https://drone.thegeeklab.de/thegeeklab/hugo-geekdoc)
[![Hugo Version](https://img.shields.io/badge/hugo-0.83-blue.svg)](https://gohugo.io)
[![GitHub release](https://img.shields.io/github/v/release/thegeeklab/hugo-geekdoc)](https://github.com/thegeeklab/hugo-geekdoc/releases/latest)
[![GitHub contributors](https://img.shields.io/github/contributors/thegeeklab/hugo-geekdoc)](https://github.com/thegeeklab/hugo-geekdoc/graphs/contributors)
[![License: MIT](https://img.shields.io/github/license/thegeeklab/hugo-geekdoc)](https://github.com/thegeeklab/hugo-geekdoc/blob/main/LICENSE)

Geekdoc is a simple Hugo theme for documentations. It is intentionally designed as a fast and lean theme and may not fit the requirements of complex projects. If a more feature-complete theme is required there are a lot of got alternatives out there. You can find a demo and the full documentation at [https://geekdocs.de](https://geekdocs.de).

![Desktop and mobile preview](https://raw.githubusercontent.com/thegeeklab/hugo-geekdoc/main/images/readme.png)

## Build and release process

This theme is subject to a CI driven build and release process common for software development. During the release build, all necessary assets are automatically built by [gulp](https://gulpjs.com/) and bundled in a release tarball. You can download the latest release from the GitHub [release page](https://github.com/thegeeklab/hugo-geekdoc/releases).

Due to the fact that `gulp` is used as pre-processor the theme cannot be used from the main branch by default. If you want to use the theme from a cloned branch instead of a release tarball you'll need to install `gulp` locally and run the default pipeline once to create all required assets.

```Shell
# install required packages from package.json
npm install

# run gulp pipeline to build required assets
npx gulp default
```

See the [Getting Started Guide](https://geekdocs.de/usage/getting-started/) for details about the different setup options.

## Contributors

Special thanks goes to all [contributors](https://github.com/thegeeklab/hugo-geekdoc/graphs/contributors). If you would like to contribute,
please see the [instructions](https://github.com/thegeeklab/hugo-geekdoc/blob/main/CONTRIBUTING.md).

Geekdoc is inspired and partially based on the [hugo-book](https://github.com/alex-shpak/hugo-book) theme, thanks [Alex Shpak](https://github.com/alex-shpak/) for your work.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/thegeeklab/hugo-geekdoc/blob/main/LICENSE) file for details.

The used SVG icons and generated icon fonts are licensed under the license of the respective icon pack:

- Font Awesome: [CC BY 4.0 License](https://github.com/FortAwesome/Font-Awesome#license)
- IcoMoon Free Pack: [GPL/CC BY 4.0](https://icomoon.io/#icons-icomoon)
- Material Icons: [Apache License 2.0](https://github.com/google/material-design-icons/blob/main/LICENSE)

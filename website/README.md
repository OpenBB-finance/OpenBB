# OpenBB Documentation Website

This repository contains the source code for the OpenBB Documentation Website. 

The website was built using [Docusaurus](https://docusaurus.io/), a modern static website generator and [TailwindCSS](https://tailwindcss.com) as styling solution.
The final website can be found at [https://docs.openbb.co](https://docs.openbb.co).


## Folder Structure

```bash
website
├── content # Markdown files
| ├── sdk # SDK markdown files
| └── terminal # Terminal markdown files
├── old_content # previous terminal documentation; required to get the examples for terminal reference
├── src # react stuff for website
├── static # Static files
├── generate_sdk_markdown.py # Script to generate markdown files for SDK
└── generate_terminal_markdown.py # Script to generate markdown files for Terminal
```

### Markdown files

The markdown files are used to generate the website. The markdown files are located in the `content` folder. The markdown files are generated using the `generate_sdk_markdown.py` and `generate_terminal_markdown.py` scripts. The markdown files are generated from the docstrings in the SDK and Terminal code. Files inside `content/sdk/reference` and `content/terminal/reference` should not be changed manually because they are generated automatically on every commit.


## Run locally

### Prerequisites

- [Node.js](https://nodejs.org/en/) >= 16.13.0
To check if you have Node.js installed, run this command in your terminal:

```bash
node --version # should be v16.13.0 or higher
```

### Install dependencies

```bash
npm install
```

### Start development server

```bash
npm start
```

This command starts a local development server and open up a browser window in `http://localhost:3000`. Most changes are reflected live without having to restart the server.

### Build

```bash
npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service. We use Github Pages to host our website. It's deployed in the `gh-pages` branch.



## Contributing

We welcome contributions to the OpenBB Documentation Website.

--- 
<details><summary>DEPRECATED - OLD README</summary>
<p>

# Hugo Server

The current features can be found in [OpenBB Terminal Features](https://openbb-finance.github.io/OpenBBTerminal).

<!-- TABLE OF CONTENTS -->
<summary><h2 style="display: inline-block">Table of Contents</h2></summary>
<ol>
  <li><a href="#install-hugo">Install Hugo</a></li>
  <li><a href="#run-locally">Run Locally</a></li>
  <li><a href="#adding-features">Adding Features</a></li>
  <ul>
    <li><a href="#structure">Structure</a></li>
    <li><a href="#new-feature">New Feature</a></li>
    </ul>
</ol>

## Install Hugo

Install [Hugo](https://gohugo.io/getting-started/installing/).

## Run Locally

Go into `website` directory with:

```bash
cd website
```

And run:

```bash
hugo server -D
```

If everything is working well, the following should appear:

```txt
13:58 $ hugo server -D
Start building sites …
hugo v0.87.0+extended darwin/amd64 BuildDate=unknown

                   | EN
-------------------+------
  Pages            | 853
  Paginator pages  |   0
  Non-page files   |   1
  Static files     | 111
  Processed images |   4
  Aliases          |   0
  Sitemaps         |   1
  Cleaned          |   0

Built in 14912 ms
Watching for changes in /Users/DidierRodriguesLopes/Documents/git/OpenBBTerminal/website/{archetypes,assets,content,data,static,themes}
Watching for config changes in /Users/DidierRodriguesLopes/Documents/git/OpenBBTerminal/website/config.toml
Environment: "development"
Serving pages from memory
Running in Fast Render Mode. For full rebuilds on change: hugo server --disableFastRender
Web Server is available at http://localhost:1313/ (bind address 127.0.0.1)
Press Ctrl+C to stop
```

And you should be able to access your local version at http://localhost:1313/.

This will be important for the addition of features to the Hugo Server.

## Adding Features

### Structure

This is the structure that the documentation follows:

```txt
website/content/_index.md
               /stocks/_index.md
                      /load/_index.md
                      /candle/_index.md
                      /discovery/_index.md
                                /ipo/_index.md
                                    /...
                                /...
                      /...
               /cryptocurrency/_index.md
                              /chart/_index.md
                              /defi/_index.md
                                   /borrow/_index.md
                                   /...
                              /...
               /...
               /common/_index.md
                      /technical_analysis/_index.md
                                         /ema/_index.md
                                         /...
                      /...
```

Note that the `common` folder holds features that are common across contexts, e.g. `technical analysis` can be performed on both `stocks` or `crytpo`.

### New Feature

To add a new command, there are two main actions that need to be done:

1. Create a directory with the name of the command and a `_index.md` file within. Examples:

   - When adding `ipo`, since this command belongs to context `stocks` and category `discovery`, we added a `ipo` folder with a `_index.md` file within to `website/content/stocks/discovery`.
   - When adding `candle`, since this command belongs to context `stocks`, we added a `candle` folder with a `_index.md` file within to `website/content/stocks/`.

2. The `_index.md` file should have the output of the `command -h` followed by a screenshot example (with white background) of what the user can expect. Note that you can now drag and drop the images while editing the readme file on the remote web version of your PR branch. Github will create a link for it with format (https://user-images.githubusercontent.com/***/***.file_format).

Example:

---

```shell
usage: ipo [--past PAST_DAYS] [--future FUTURE_DAYS]
```

Past and future IPOs. [Source: https://finnhub.io]

- --past : Number of past days to look for IPOs. Default 0.
- --future : Number of future days to look for IPOs. Default 10.

<IMAGE HERE - Use drag and drop hint mentioned above>

---

3. Update the Navigation bar to match the content you've added. This is done by adding 2 lines of code to `website/data/menu/`, i.e. a `name` and a `ref`. Example:

```
---
main:
  - name: stocks
    ref: "/stocks"
    sub:
      - name: load
        ref: "/stocks/load"
      - name: candle
        ref: "/stocks/candle"
      - name: discovery
        ref: "/stocks/discovery"
        sub:
          - name: ipo
            ref: "/stocks/discovery/ipo"
          - name: map
            ref: "/stocks/discovery/map"
```

</p>
</details>

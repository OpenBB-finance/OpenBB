# OpenBB Documentation Website

This repository contains the source code for the OpenBB Documentation Website.

The website was built using [Docusaurus](https://docusaurus.io/), a modern static website generator and [TailwindCSS](https://tailwindcss.com) as styling solution. It uses algolia search for the search bar.
The final website can be found at [https://docs.openbb.co](https://docs.openbb.co).

## Folder Structure

```bash
website
├── content # Markdown files
| ├── sdk # SDK markdown files
| ├── bot # bot markdown files
| ├── platform # platform markdown files
| └── terminal # Terminal markdown files
├── src # react stuff for website
├── static # Static files
├── generate_sdk_markdown.py # Script to generate markdown files for SDK
└── generate_terminal_markdown.py # Script to generate markdown files for Terminal
```

### Markdown files

The markdown files are used to generate the website. The markdown files are located in the `content` folder. The markdown files are generated using the `generate_sdk_markdown.py` and `generate_terminal_markdown.py` scripts. The markdown files are generated from the docstrings in the SDK and Terminal code. Files inside `content/sdk/reference` and `content/terminal/reference` should not be changed manually because they are generated automatically on every commit.

### Syntax sugar

#### Code blocks

Code blocks are generated using the default markdown syntax:

  ```python
  print("Hello World")
  ```

To generate a dynamic date for a certain code block (useful for options examples that need to have a valid date), you can use `2022-07-29` as a placeholder. The script will replace it with the third friday of the next month.

```txt
/op oichart ticker:AMD expiry:2022-07-29
```

#### Available options

This is great for huge lists. It opens a popup that contains the list and the search bar, so you can easily find what you are looking for. Everything is virtualized, so it's always fast no matter how many items you have.
Check [crypto page](https://docs.openbb.co/bot/discord/crypto) for a demo of this component.

```md
import AvailableOptions from "@site/src/components/General/AvailableOptions";

<AvailableOptions
label="Exchanges"
allOptions={[
"aax",
"ascendex",
"bequant",
"bibox",
"bigone",
"binance",
"binancecoinm",
"binanceus",
"binanceusdm",
"bit2c",
"bitbank",
"bitbay",
"bitcoincom",
"bitfinex",
"bitfinex2",
"bitflyer",
"bitforex",
"bitget",
"bithumb",
"bitmart",
"bitmex",
"bitopro",
"bitpanda",
"bitrue",
"bitso",
"bitstamp",
"bitstamp1",
"bittrex",
"bitvavo",
]}
/>
```

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

## Run tests

```bash
pytest tests/website --autodoc
```

> If tests are run locally, the `--autodoc` flag is required, otherwise tests will be skipped.

> To install necessary dependencies for tests, run `poetry install -E doc` in the root directory of the repository.

## Notes

### iFrame

We are detecting whether the website is loaded inside an iframe. If it is, we are hiding the header and footer. This is done to have a better integration with out [hub website](https://my.openbb.co).

## Contributing

We welcome contributions to the OpenBB Documentation Website.

---

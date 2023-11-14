// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require("prism-react-renderer/themes/vsLight");
const darkCodeTheme = require("prism-react-renderer/themes/vsDark");
const math = require("remark-math");
const katex = require("rehype-katex");

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "OpenBB Docs",
  tagline: "OpenBB Docs",
  url: "https://docs.openbb.co", // Your website URL
  baseUrl: "/",
  projectName: "OpenBBTerminal",
  organizationName: "OpenBB-finance",
  trailingSlash: false,
  onBrokenLinks: "warn",
  onBrokenMarkdownLinks: "warn",
  favicon: "img/favicon.ico",

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },
  plugins: [
    [
      "@docusaurus/plugin-client-redirects",
      {
        redirects: [
          {
            from: "/terminal/menus/forecasting",
            to: "/terminal/menus/forecast",
          },
        ],
      },
    ],
    async function twPlugin(context, options) {
      return {
        name: "docusaurus-tailwindcss",
        configurePostCss(postcssOptions) {
          // Appends TailwindCSS and AutoPrefixer.
          postcssOptions.plugins.push(require("tailwindcss"));
          postcssOptions.plugins.push(require("autoprefixer"));
          return postcssOptions;
        },
      };
    },
    /*[
      "@docusaurus/plugin-content-docs",
      {
        id: "sdk",
        path: "content/sdk",
        routeBasePath: "sdk",
        editUrl:
          "https://github.com/OpenBB-finance/OpenBBTerminal/edit/main/website/",
        sidebarPath: require.resolve("./sidebars.js"),
      },
    ],
    [
      "@docusaurus/plugin-content-docs",
      {
        id: "bot",
        path: "content/bot",
        routeBasePath: "bot",
        editUrl:
          "https://github.com/OpenBB-finance/OpenBBTerminal/edit/main/website/",
        sidebarPath: require.resolve("./sidebars.js"),
      },
    ],*/
  ],
  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
          editUrl: "https://github.com/OpenBB-finance/OpenBBTerminal/edit/main/website/",
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
          routeBasePath: "/",
          path: "content",
          remarkPlugins: [math],
          rehypePlugins: [katex],
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: "img/banner.png",
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
      // TODO - Jose can you make this so we get lighter color on main view - like bot docs
      colorMode: {
        defaultMode: "dark",
        disableSwitch: false,
        respectPrefersColorScheme: false,
      },
      algolia: {
        appId: "7D1HQ0IXAS",
        apiKey: "a2e289977b4b663ed9cf3d4635a438fd",  // pragma: allowlist secret
        indexName: "openbbterminal",
        contextualSearch: false,
      },
    }),
  stylesheets: [
    {
      href: "/katex/katex.min.css",
      type: "text/css",
    },
  ],
};

module.exports = config;

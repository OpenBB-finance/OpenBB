// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

import { Options, ThemeConfig } from "@docusaurus/preset-classic";
import { Config } from "@docusaurus/types";
import autoprefixer from "autoprefixer";
import { themes } from "prism-react-renderer";
import katex from "rehype-katex";
import math from "remark-math";
import tailwind from "tailwindcss";

export default {
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
          postcssOptions.plugins.push(tailwind);
          postcssOptions.plugins.push(autoprefixer);
          return postcssOptions;
        },
      };
    },
  ],
  presets: [
    [
      "classic",
      {
        docs: {
          sidebarPath: "./sidebars.js",
          editUrl:
            "https://github.com/OpenBB-finance/OpenBBTerminal/edit/main/website/",
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
          routeBasePath: "/",
          path: "content",
          remarkPlugins: [math],
          rehypePlugins: [katex],
        },
        theme: {
          customCss: "./src/css/custom.css",
        },
      } satisfies Options,
    ],
  ],

  themeConfig: {
    image: "img/banner.png",
    prism: {
      theme: themes.vsLight,
      darkTheme: themes.vsDark,
    },
    // TODO - Jose can you make this so we get lighter color on main view - like bot docs
    colorMode: {
      defaultMode: "dark",
      disableSwitch: false,
      respectPrefersColorScheme: false,
    },
    algolia: {
      appId: "7D1HQ0IXAS",
      apiKey: "a2e289977b4b663ed9cf3d4635a438fd", // pragma: allowlist secret
      indexName: "openbbterminal",
      contextualSearch: false,
    },
  } satisfies ThemeConfig,
  stylesheets: [
    {
      href: "/katex/katex.min.css",
      type: "text/css",
    },
  ],
} satisfies Config;

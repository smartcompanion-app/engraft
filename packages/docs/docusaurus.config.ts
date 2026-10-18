import type * as Preset from "@docusaurus/preset-classic";
import type { Config } from "@docusaurus/types";
import { themes as prismThemes } from "prism-react-renderer";

const repo = "https://github.com/smartcompanion-app/engraft";

const config: Config = {
  title: "engraft",
  tagline: "Apply customizations to any project without templating placeholders",
  favicon: "engraft-icon.svg",

  url: "https://smartcompanion-app.github.io",
  baseUrl: "/engraft/",
  organizationName: "smartcompanion-app",
  projectName: "engraft",
  trailingSlash: false,

  onBrokenLinks: "throw",
  onBrokenAnchors: "throw",

  // The logo, wordmark and icon live once, at the repository root, so the
  // README and the site can never show different versions of them.
  staticDirectories: ["../../assets"],

  markdown: {
    // The pages are plain Markdown that also has to read well on GitHub, so
    // .md files are parsed as CommonMark rather than MDX: a `<` or `{` in prose
    // stays text instead of becoming JSX.
    format: "detect",
    hooks: { onBrokenMarkdownLinks: "throw" },
  },

  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      {
        docs: {
          path: "docs",
          routeBasePath: "/",
          sidebarPath: "./sidebars.ts",
          editUrl: `${repo}/edit/main/packages/docs/`,
        },
        blog: false,
        theme: {
          customCss: "./src/css/custom.css",
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: "engraft-social-card.png",
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: "engraft",
      logo: {
        alt: "engraft",
        src: "engraft-mark.svg",
        srcDark: "engraft-mark-dark.svg",
      },
      items: [
        { type: "docSidebar", sidebarId: "docs", position: "left", label: "Docs" },
        {
          href: "https://www.npmjs.com/package/@smartcompanion/engraft",
          label: "npm",
          position: "right",
        },
        { href: repo, label: "GitHub", position: "right" },
      ],
    },
    footer: {
      style: "dark",
      logo: {
        alt: "engraft",
        src: "engraft-logo-dark.svg",
        height: 36,
      },
      links: [
        {
          title: "Docs",
          items: [
            { label: "Getting started", to: "/getting-started" },
            { label: "Actions", to: "/actions" },
            { label: "CLI reference", to: "/cli" },
          ],
        },
        {
          title: "Project",
          items: [
            { label: "GitHub", href: repo },
            { label: "npm", href: "https://www.npmjs.com/package/@smartcompanion/engraft" },
            { label: "Changelog", href: `${repo}/blob/main/packages/engraft/CHANGELOG.md` },
          ],
        },
      ],
      copyright: `BSD 2-Clause · <a href="https://smartcompanion.app">SmartCompanion</a>`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.vsDark,
      additionalLanguages: ["bash", "diff", "yaml", "json"],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;

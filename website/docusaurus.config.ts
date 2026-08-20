import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Internacia DB',
  tagline: 'Reference data for countries, organizations, and country groups',
  favicon: 'img/favicon.svg',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://datenoio.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/internacia-db/',
  trailingSlash: true,

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'datenoio', // Usually your GitHub org/user name
  projectName: 'internacia-db', // Usually your repo name.

  // Your markdown references repo-root files (e.g. ../llms.txt, ../ATTRIBUTION.md).
  // Those aren’t always present in Docusaurus’ content pipeline, so start lenient.
  onBrokenLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if you are writing a site
  // in Chinese, you may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Use the repo’s existing Markdown docs as the Docusaurus content source.
          // (We keep the scaffold’s default website/docs unused.)
          path: '../docs',
          routeBasePath: '/docs',
          editUrl: 'https://github.com/datenoio/internacia-db/edit/main/docs/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/logo.png',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Internacia DB',
      logo: {
        alt: 'Internacia DB',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'mainSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          href: 'https://github.com/datenoio/internacia-db',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Getting started',
              to: '/docs/getting-started',
            },
            {
              label: 'Query examples',
              to: '/docs/query-examples',
            },
            {
              label: 'AI consumers',
              to: '/docs/ai-consumers',
            },
            {
              label: 'Data dictionary',
              to: '/docs/data-dictionary',
            },
          ],
        },
        {
          title: 'Dateno',
          items: [
            {
              label: 'Dateno',
              href: 'https://dateno.io',
            },
            {
              label: 'internacia-api',
              href: 'https://github.com/datenoio/internacia-api',
            },
            {
              label: 'internacia-python',
              href: 'https://github.com/datenoio/internacia-python',
            },
          ],
        },
        {
          title: 'License',
          items: [
            {
              label: 'Code: MIT',
              href: 'https://github.com/datenoio/internacia-db/blob/main/LICENSE',
            },
            {
              label: 'Data & docs: CC BY 4.0',
              href: 'https://github.com/datenoio/internacia-db/blob/main/DATA_LICENSE',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Dateno. Internacia is part of the Dateno open-source project. Code is MIT; data and documentation are CC BY 4.0.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
    mermaid: {
      theme: {light: 'neutral', dark: 'dark'},
    },
  } satisfies Preset.ThemeConfig,
};

export default config;

import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  mainSidebar: [
    {
      type: 'category',
      label: 'Overview',
      items: [
        'getting-started',
        'architecture',
        'topic-taxonomy',
        'strategy-and-user-needs',
        'release-distribution',
        'when-to-use-internacia',
      ],
    },
    {
      type: 'category',
      label: 'Data contracts & policies',
      items: [
        'ai-consumers',
        'llm-scenarios',
        'data-dictionary',
        'enrichment',
        'improvement-plan',
        'country-code-policy',
        'entity-classification-policy',
        'intblock-inclusion-policy',
      ],
    },
    {
      type: 'category',
      label: 'Verified query examples',
      items: [
        'query-examples',
        'query-examples-polars',
        'query-examples-r',
        'query-examples-observable',
        'query-examples.zh',
      ],
    },
    {
      type: 'category',
      label: 'Agent workflows',
      items: [
        'agents/query',
        'agents/contribute',
        'agents/openspec-quickstart',
      ],
    },
    {
      type: 'category',
      label: '中文入口',
      items: ['agents/zh/query', 'agents/zh/contribute'],
    },
  ],

  // But you can create a sidebar manually
  /*
  mainSidebar: [
    'intro',
    'hello',
    {
      type: 'category',
      label: 'Tutorial',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
   */
};

export default sidebars;

import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type DocLink = {
  to: string;
  label: string;
  description: string;
};

type DocSection = {
  title: string;
  items: DocLink[];
};

const sections: DocSection[] = [
  {
    title: 'Overview',
    items: [
      {
        to: '/docs/getting-started',
        label: 'Getting started',
        description: 'Spreadsheet, DuckDB, and SDK paths into the datasets.',
      },
      {
        to: '/docs/when-to-use-internacia',
        label: 'When to use Internacia',
        description: 'Task-based routing for whether this data fits the job.',
      },
      {
        to: '/docs/architecture',
        label: 'Architecture',
        description: 'Source YAML, validation, enrichment, and export pipeline.',
      },
      {
        to: '/docs/release-distribution',
        label: 'Release distribution',
        description: 'GitHub Releases, Zenodo, and Hugging Face mirrors.',
      },
      {
        to: '/docs/topic-taxonomy',
        label: 'Topic taxonomy',
        description: 'How intblock topic keys are added, merged, and deprecated.',
      },
      {
        to: '/docs/strategy-and-user-needs',
        label: 'Strategy and user needs',
        description: 'Who uses Internacia and what the product should serve.',
      },
    ],
  },
  {
    title: 'Data contracts & policies',
    items: [
      {
        to: '/docs/ai-consumers',
        label: 'AI consumer guide',
        description: 'Join keys, scope boundaries, and consumption contract.',
      },
      {
        to: '/docs/data-dictionary',
        label: 'Data dictionary',
        description: 'Field-level reference for exported tables.',
      },
      {
        to: '/docs/llm-scenarios',
        label: 'LLM scenarios',
        description: 'Copy/paste lookup and join patterns for generated code.',
      },
      {
        to: '/docs/country-code-policy',
        label: 'Country code policy',
        description: 'ISO vs user-assigned codes and entity status.',
      },
      {
        to: '/docs/entity-classification-policy',
        label: 'Entity classification',
        description: 'TW, PS, XK, EH and other edge-case modeling rules.',
      },
      {
        to: '/docs/intblock-inclusion-policy',
        label: 'Intblock inclusion',
        description: 'What belongs in intblocks and scope_category values.',
      },
      {
        to: '/docs/enrichment',
        label: 'Enrichment',
        description: 'World Bank, Wikidata, and timezone refresh workflow.',
      },
      {
        to: '/docs/improvement-plan',
        label: 'Improvement plan',
        description: 'Engineering backlog and quality workstreams.',
      },
    ],
  },
  {
    title: 'Verified query examples',
    items: [
      {
        to: '/docs/query-examples',
        label: 'DuckDB / SQL',
        description: 'UN membership, borders, org density, former members.',
      },
      {
        to: '/docs/query-examples-polars',
        label: 'Polars',
        description: 'The same recipes against Parquet with Polars.',
      },
      {
        to: '/docs/query-examples-r',
        label: 'R / dplyr',
        description: 'Arrow and dplyr recipes against Parquet.',
      },
      {
        to: '/docs/query-examples-observable',
        label: 'Observable / Plot',
        description: 'DuckDB-Wasm notebooks and Observable Plot charts.',
      },
      {
        to: '/docs/query-examples.zh',
        label: '查询示例（中文）',
        description: '已验证的中文 DuckDB 查询场景。',
      },
    ],
  },
  {
    title: 'Agent workflows',
    items: [
      {
        to: '/docs/agents/query',
        label: 'Query workflow',
        description: 'Look up countries, borders, and org membership.',
      },
      {
        to: '/docs/agents/contribute',
        label: 'Contribute workflow',
        description: 'Edit country and intblock YAML safely.',
      },
      {
        to: '/docs/agents/openspec-quickstart',
        label: 'OpenSpec quickstart',
        description: 'Schema changes and breaking exports.',
      },
    ],
  },
  {
    title: '中文入口',
    items: [
      {
        to: '/docs/agents/zh/query',
        label: '查询工作流',
        description: '国家、边界、组织成员关系查询。',
      },
      {
        to: '/docs/agents/zh/contribute',
        label: '贡献工作流',
        description: '安全编辑国家与 intblock YAML。',
      },
    ],
  },
];

function DocItem({to, label, description}: DocLink) {
  return (
    <li className={styles.item}>
      <Link className={styles.itemLink} to={to}>
        <span className={styles.itemLabel}>{label}</span>
        <span className={styles.itemDescription}>{description}</span>
      </Link>
    </li>
  );
}

export default function DocsContents(): ReactNode {
  return (
    <section className={styles.contents}>
      <div className="container">
        <Heading as="h2" className={styles.contentsTitle}>
          Documentation contents
        </Heading>
        <div className={styles.grid}>
          {sections.map((section) => (
            <section key={section.title} className={styles.section}>
              <Heading as="h3" className={styles.sectionTitle}>
                {section.title}
              </Heading>
              <ul className={styles.list}>
                {section.items.map((item) => (
                  <DocItem key={item.to} {...item} />
                ))}
              </ul>
            </section>
          ))}
        </div>
      </div>
    </section>
  );
}

# Internacia DB — AI 智能体指南（中文）

结构化参考数据：**256** 个国家/地区、**1318** 个国际组织/集团（intblocks）、**82** 种 blocktype 分类。
[Dateno](https://dateno.io) 开源项目的一部分。数据与文档许可：CC-BY-4.0；代码：MIT。

English: [AGENTS.md](AGENTS.md)

## 你需要做什么？

| 目标 | 从这里开始 | 不要 |
|------|------------|------|
| **查询、关联、下游 enrichment** | [llms.zh.txt](llms.zh.txt) → [docs/ai-consumers.md](docs/ai-consumers.md) | 解析 `data/countries/`、`data/intblocks/` 下的源 YAML |
| **查国家、边界、组织成员** | [docs/agents/zh/query.md](docs/agents/zh/query.md) | 用 `includes[].name` 做关联（应用 `includes[].id`） |
| **编辑国家或 intblock YAML** | [docs/agents/zh/contribute.md](docs/agents/zh/contribute.md) | 手改 `data/datasets/`（仅构建生成） |
| **查找缺失 intblock / 改进已有记录** | [docs/discovery.md](docs/discovery.md) → [docs/agents/discover.md](docs/agents/discover.md) | 整库导入外部目录 |
| **已检索过哪些目录** | [docs/intblock-sources.md](docs/intblock-sources.md) | 把目录索引卡当作成员名录来源 |
| **改 schema、新能力、破坏性导出** | [docs/agents/openspec-quickstart.md](docs/agents/openspec-quickstart.md) | 未批准前先实现 |

## 推荐数据访问方式

- **先构建：** 生成的导出文件不提交到仓库；请运行 `python scripts/builder.py build`（约 1 分钟），或从最新 GitHub Release 下载 `internacia.duckdb`。
- **DuckDB：** `data/datasets/internacia.duckdb`（表：`countries`、`intblocks`、`blocktypes`、`memberships`、`_meta`、别名表及 `border_status`；视图：`current_memberships`、`country_currencies`、`country_languages`、`country_timezones`、`country_borders`，见 [数据契约](docs/data-contract.md)）
- **Parquet：** `data/datasets/{countries,intblocks,blocktypes,memberships}.parquet`
- **远程：** [internacia-python](https://github.com/datenoio/internacia-python)（SDK；PyPI 上的 0.2.x 早于数据 v3，见 [SDK status](docs/llm-scenarios.md#sdk-status)）。[internacia-api](https://github.com/datenoio/internacia-api) **开发中**，仅自托管 — 无公开 HTTP 实例。

升级前检查版本：`SELECT dataset, version, schema_hash FROM _meta;` 或读 `data/datasets/*.manifest.json`。

## 关联键与易错点

- 国家：主键 `code`（ISO alpha-2），另有 `iso3code`、`wikidata_id`
- 组织：主键 `id`（大写，如 `NATO`、`EU`）；成员通过 `includes[].id` → 国家 `code`
- **`borders` 使用 alpha-3**，不是 alpha-2 — 用 `iso3code` 关联
- **`population` / `area` / `gini` 是结构体** — 数值用 `.value`；未知年份用 `null`，**不要用 0**
- 当前 ISO 正式国家（249 条）：`code_status = 'official_iso3166_1'`
- intblock id 更名：查 `data/datasets/intblocks_aliases.json`

## 禁止事项（范围护栏）

- **不要** 给 countries 添加 HDI、GDP、政体、互联网普及率等社会经济画像字段
- **不要** 把全部 256 个 code 都当作正式 ISO — 需按 `code_status` 过滤
- **不要** 把 World Bank `region` / `incomeLevel` 缺失当作数据错误（8 个实体无 `region`/`incomeLevel`/`lendingType`；共 119 条记录按设计无 `adminregion`：即这 8 个实体加 111 个高收入经济体）

## 校验（贡献者）

```bash
python scripts/validate_countries.py          # 人类可读输出
python scripts/validate_countries.py --json   # 智能体结构化输出
python scripts/validate_intblocks.py --json
pytest tests/
```

## 查询示例

已验证的 DuckDB 示例：[docs/query-examples.zh.md](docs/query-examples.zh.md)（由 `tests/test_documented_queries_zh.py` 覆盖）。

## 平台适配（薄封装）

- [CLAUDE.md](CLAUDE.md) — Claude Code（英文）
- [.github/copilot-instructions.md](.github/copilot-instructions.md) — GitHub Copilot（英文）
- [.kimi/AGENTS.md](.kimi/AGENTS.md) — Kimi Code 补充说明
- [.lingma/rules/](.lingma/rules/) — 通义灵码项目规则
- [llms.zh.txt](llms.zh.txt) — 中文紧凑索引

<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines
- **Countries dataset scope**: reference data only — do not add socioeconomic profile fields (HDI, GDP, government type, etc.)

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

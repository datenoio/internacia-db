# 智能体指南：查询 Internacia 数据

面向 Kimi K3、GLM-5.2、通义灵码、Qoder 等中文 LLM 的跨平台查询流程。
English: [../query.md](../query.md)

## 查询前必读

1. 读 [llms.zh.txt](../../../llms.zh.txt) — 关联键与易错点。
2. 使用导出数据集 — **除非在编辑数据，否则不要** 解析 `data/countries/*.yaml` 或 `data/intblocks/**/*.yaml`。
3. 完整消费契约：[ai-consumers.md](../../ai-consumers.md)（英文）。
4. 已验证示例：[query-examples.zh.md](../../query-examples.zh.md)（中文）；英文示例：
   [query-examples.md](../../query-examples.md)（DuckDB）、
   [query-examples-polars.md](../../query-examples-polars.md)（Polars / Parquet）、
   [query-examples-r.md](../../query-examples-r.md)（R / dplyr）、
   [query-examples-observable.md](../../query-examples-observable.md)（Observable / Plot）。

## 访问路径

| 方式 | 路径 / URL |
|------|------------|
| DuckDB（推荐） | 运行 `python scripts/builder.py build` 后的 `data/datasets/internacia.duckdb`，或最新 Release 资产（导出文件不提交到仓库） |
| Parquet | `data/datasets/countries.parquet`、`intblocks.parquet`、`blocktypes.parquet`、`memberships.parquet`、`trade_agreements.parquet`、`trade_agreement_parties.parquet`、`trade_agreement_instruments.parquet` |
| 版本检查 | `SELECT * FROM _meta;` 或 `data/datasets/*.manifest.json` |
| Python SDK（无需完整 checkout） | https://github.com/datenoio/internacia-python（PyPI 上的 `internacia` 0.5.0 只读数据契约 3.x 和 4.x，不读当前的 5.x，见 [SDK status](../../llm-scenarios.md#sdk-status)） |
| HTTP API | https://github.com/datenoio/internacia-api（**开发中**，仅自托管；无公开托管实例） |

## 关联键

| 实体 | 主键 | 备注 |
|------|------|------|
| 国家 | `code`（alpha-2） | 另有 `iso3code`、`numeric_code`、`wikidata_id` |
| 组织 | `id` | 如 `NATO`、`EU`、`UN`；另有 `wikidata_id`、`blocktype`、`partof` |
| 成员 | `includes[].id` → 国家 `code` | **不要用** `includes[].name` |
| Blocktype 分类 | `blocktypes.id` | 对应 `intblocks.blocktype` 列表中的值 |
| 边界 | `borders` 中的 alpha-3 | 与邻国 `iso3code` 关联 |
| 贸易协定 | `trade_agreements.id` | `intblock_id`（3 方及以上协定的成员名录）、`wto_rta_id`、`dta_id` |
| 协定缔约方 | `trade_agreement_parties.party_id` | 按 `party_type` 对应国家 `code` 或 intblock `id` |

## 范围

**在范围内：** ISO 标识、地理、带来源/年份的人口/面积、世界银行分类、语言/货币/时区、组织成员、贸易与投资协定（缔约方、状态、日期）、Wikidata。

**不在范围内：** HDI、GDP、政体、互联网普及率、时间序列指标 — 请下游数据集 enrichment。

## 中文场景查询（DuckDB）

### 版本与 schema

```sql
SELECT dataset, version, schema_hash, build_date FROM _meta;
```

### 按中文名查国家（other_names.id = 'zh'）

```sql
SELECT c.code, c.name, oname.name AS zh_name
FROM countries c, UNNEST(c.other_names) AS t(oname)
WHERE oname.id = 'zh' AND oname.name = '中华人民共和国';
```

### 泰国的陆地邻国

`borders` 存 alpha-3，用 `iso3code` 关联：

```sql
SELECT n.code, n.name
FROM countries th,
     UNNEST(th.borders) AS b(neighbor_iso3)
JOIN countries n ON n.iso3code = b.neighbor_iso3
WHERE th.code = 'TH'
ORDER BY n.name;
```

### 北约（NATO）成员国

```sql
SELECT m.id AS member_code, m.name AS member_label, m.status
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE i.id = 'NATO' AND m.type = 'country'
ORDER BY m.id;
```

### 包含老挝的组织

```sql
SELECT i.id, i.name
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE m.id = 'LA' AND m.type = 'country'
ORDER BY i.name;
```

### 当前正式 ISO 国家（249 条）

```sql
SELECT code, name FROM countries
WHERE code_status = 'official_iso3166_1'
ORDER BY code;
```

### 联合国会员国

```sql
SELECT code, name FROM countries WHERE un_member = true ORDER BY name;
```

### 国家属性字段（原 attribute intblock）

```sql
SELECT code, name FROM countries WHERE car_side = 'left';
SELECT code, name FROM countries WHERE dvd_region = 1;
SELECT c.code, c.name FROM countries c, UNNEST(c.writing_directions) t(d) WHERE d.id = 'rtl';
SELECT c.code, c.name FROM countries c, UNNEST(c.legal_systems) t(l) WHERE l.id = 'common_law';
```

请用这些字段，不要用已退役的 `LHTRAFFIC` / `DVD_*` / `WS*` / `LS*` / `*GAUGE` id；旧 id 对照：`attribute_intblock_migrations.json`。完整示例见 [query-examples.zh.md](../../query-examples.zh.md)。

### 关联前先解析 intblock 别名（Python）

```python
import json
import pandas as pd

aliases = {a["alias"]: a["target"] for a in json.load(open("data/datasets/intblocks_aliases.json"))}
blocks = pd.read_parquet("data/datasets/intblocks.parquet")
blocks["id"] = blocks["id"].map(lambda x: aliases.get(x, x))
```

`reason = 'moved'` 的别名 `target_dataset` 为 `trade_agreements`：该 id 已移入贸易协定注册表。

### 结构化人口字段（Pandas — `.struct` 需要 Arrow dtype backend）

```python
df = pd.read_parquet("data/datasets/countries.parquet", dtype_backend="pyarrow")
pop = df["population"].struct.field("value")
```

## 贸易协定

贸易与投资协定在注册表 `trade_agreements`、`trade_agreement_parties`、`trade_agreement_instruments`
三张表中，另有视图 `country_trade_agreements`（每个国家与现行协定一行；EU 等集团缔约方展开为其当前成员，
`via = 'EU'`）。双边 FTA 只在注册表中：自 5.0.0 起它们不再是 intblock。统计贸易协定时请过滤
`agreement_type`，因为投资条约、贸易关系协定与优惠安排共用这张表。

```sql
SELECT c.agreement_id, c.agreement_type, c.via
FROM country_trade_agreements c
WHERE c.country_code = 'CL' AND c.agreement_status = 'in_force'
  AND c.agreement_type NOT IN ('investment', 'trade_relations', 'preference_scheme')
ORDER BY c.agreement_id;
```

字段含义：[ai-consumers.md](../../ai-consumers.md#trade-agreements-registry)（英文）；
更多 SQL：[llm-scenarios.md](../../llm-scenarios.md#29-trade-agreements-of-a-country)（英文）。

## 常见错误

| 错误 | 正确做法 |
|------|----------|
| 用 alpha-2 关联 borders | 用 alpha-3，关联 `iso3code` |
| 用 `includes[].name` 关联成员 | 用 `includes[].id`（国家 code） |
| 认为 256 个 code 都是正式 ISO | 过滤 `code_status = 'official_iso3166_1'` |
| 从 `population` 读 plain number | 用结构体 `.value`（pandas：`dtype_backend="pyarrow"`；Polars：`.struct.field("value")`） |
| 在本数据集找 GDP/HDI | 超出范围，请下游 enrichment |
| 中文模糊匹配 includes[].name | 成员关联只用 `includes[].id` |
| 忽略别名重映射 | 按 intblock `id` 关联前先加载 `intblocks_aliases.json` |
| 在 `intblocks` 里找双边 FTA | 查 `trade_agreements` / `country_trade_agreements`；`reason = 'moved'` 的别名指向那里 |

## DuckDB 结构体列表

展开 list-of-struct 列：`UNNEST(i.includes) AS t(m)`，然后引用 `m.id`、`m.type`、`m.status`。

## 相关文档

- [AGENTS.zh.md](../../../AGENTS.zh.md) — 中文路由入口
- [AGENTS.md](../../../AGENTS.md) — 英文路由入口
- [contribute.md](contribute.md) — 编辑 YAML
- [discover.md](../discover.md) — 查找缺失记录 / 改进已有 YAML（英文）
- `.agent/workflows/query-org-members.md` — 组织成员查询步骤（英文）

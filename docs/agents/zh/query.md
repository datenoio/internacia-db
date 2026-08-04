# 智能体指南：查询 Internacia 数据

面向 Kimi K3、GLM-5.2、通义灵码、Qoder 等中文 LLM 的跨平台查询流程。
English: [../query.md](../query.md)

## 查询前必读

1. 读 [llms.zh.txt](../../../llms.zh.txt) — 关联键与易错点。
2. 使用导出数据集 — **除非在编辑数据，否则不要** 解析 `data/countries/*.yaml` 或 `data/intblocks/**/*.yaml`。
3. 完整消费契约：[ai-consumers.md](../../ai-consumers.md)（英文）。
4. 已验证示例：[query-examples.zh.md](../../query-examples.zh.md)。

## 访问路径

| 方式 | 路径 / URL |
|------|------------|
| DuckDB（推荐） | `data/datasets/internacia.duckdb` |
| Parquet | `data/datasets/countries.parquet` 等 |
| 版本检查 | `SELECT * FROM _meta;` 或 `data/datasets/*.manifest.json` |
| Python SDK | https://github.com/datenoio/internacia-python |
| HTTP API | https://github.com/datenoio/internacia-api |

## 关联键

| 实体 | 主键 | 备注 |
|------|------|------|
| 国家 | `code`（alpha-2） | 另有 `iso3code`、`wikidata_id` |
| 组织 | `id` | 如 `NATO`、`EU`、`UN` |
| 成员 | `includes[].id` → 国家 `code` | **不要用** `includes[].name` |
| 边界 | `borders` 中的 alpha-3 | 与 `iso3code` 关联 |

## 范围

**在范围内：** ISO 标识、地理、带来源/年份的人口/面积、世界银行分类、语言/货币/时区、组织成员、Wikidata。

**不在范围内：** HDI、GDP、政体、互联网普及率 — 请下游数据集 enrichment。

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

### 国家属性字段（原 attribute intblock）

```sql
SELECT code, name FROM countries WHERE car_side = 'left';
SELECT code, name FROM countries WHERE dvd_region = 1;
SELECT c.code, c.name FROM countries c, UNNEST(c.writing_directions) t(d) WHERE d.id = 'rtl';
SELECT c.code, c.name FROM countries c, UNNEST(c.legal_systems) t(l) WHERE l.id = 'common_law';
```

旧 id 对照：`attribute_intblock_migrations.json`。完整示例见 [query-examples.zh.md](../../query-examples.zh.md)。

## 常见错误

| 错误 | 正确做法 |
|------|----------|
| 用 alpha-2 关联 borders | 用 alpha-3，关联 `iso3code` |
| 用 `includes[].name` 关联成员 | 用 `includes[].id`（国家 code） |
| 认为 256 个 code 都是正式 ISO | 过滤 `code_status = 'official_iso3166_1'` |
| 从 `population` 读 plain number | 用结构体 `.value` |
| 在本数据集找 GDP/HDI | 超出范围，请下游 enrichment |
| 中文模糊匹配 includes[].name | 成员关联只用 `includes[].id` |

## 相关文档

- [AGENTS.zh.md](../../../AGENTS.zh.md) — 中文路由入口
- [contribute.md](contribute.md) — 编辑 YAML
- `.agent/workflows/query-org-members.md` — 组织成员查询步骤（英文）

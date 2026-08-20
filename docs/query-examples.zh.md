# 查询示例（中文场景）

针对 `data/datasets/internacia.duckdb` 的已验证 DuckDB 示例。
字段语义与范围见 [ai-consumers.md](ai-consumers.md)；English: [query-examples.md](query-examples.md)。

```bash
duckdb data/datasets/internacia.duckdb
```

**DuckDB 结构体列表：** 使用 `UNNEST(column) AS t(row)`，再访问 `row.field`。

## 版本检查

```sql
SELECT dataset, version, schema_hash, build_date FROM _meta;
```

**预期：** 4 行（countries、intblocks、blocktypes、memberships）。

## 按中文官方名查中国

使用 `other_names` 中 `id = 'zh'` 的条目，不要用 `includes[].name`。

```sql
SELECT c.code, c.name, oname.name AS zh_official_name
FROM countries c, UNNEST(c.other_names) AS t(oname)
WHERE oname.id = 'zh' AND oname.name = '中华人民共和国';
```

**预期：** 1 行，`code = CN`。

## 当前正式 ISO 国家（249）

```sql
SELECT code, name
FROM countries
WHERE code_status = 'official_iso3166_1'
ORDER BY code;
```

**预期：** 249 行。7 个非标准 code（AN、JG、XK、XA、XS、XT、XN）被排除。

## 国家属性字段（原 attribute intblock）

驾驶侧、书写方向/系统、DVD 区、广播制式、法律传统、轨距现为 countries 列。
旧 intblock id 对照见 `attribute_intblock_migrations.json`。

### 左侧通行

```sql
SELECT code, name
FROM countries
WHERE car_side = 'left'
ORDER BY code;
```

**预期：** 74 行。

### 从右到左书写方向

```sql
SELECT c.code, c.name, d.id AS direction
FROM countries c, UNNEST(c.writing_directions) AS t(d)
WHERE d.id = 'rtl'
ORDER BY c.code;
```

**预期：** 28 行。SQL 中需引用 `"primary"`（保留字）。

### 西里尔字母书写系统

```sql
SELECT c.code, c.name, s.id AS script
FROM countries c, UNNEST(c.writing_systems) AS t(s)
WHERE s.id = 'cyrillic'
ORDER BY c.code;
```

**预期：** 12 行。覆盖面较稀疏（约 58 条有值）；词表见 `data/vocabs/`。

### DVD 区域 1

```sql
SELECT code, name, dvd_region
FROM countries
WHERE dvd_region = 1
ORDER BY code;
```

**预期：** 8 行（含 `US`、`CA`）。

## 泰国的陆地邻国

`borders` 存 alpha-3，与 `iso3code` 关联。

```sql
SELECT n.code, n.name
FROM countries th,
     UNNEST(th.borders) AS b(neighbor_iso3)
JOIN countries n ON n.iso3code = b.neighbor_iso3
WHERE th.code = 'TH'
ORDER BY n.name;
```

**预期：** 4 行（柬埔寨、老挝、缅甸、马来西亚）。

## 北约（NATO）成员国

```sql
SELECT m.id AS member_code, m.name AS member_label
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE i.id = 'NATO' AND m.type = 'country'
ORDER BY m.id;
```

**预期：** 32 行。

## 包含老挝（LA）的组织

```sql
SELECT i.id, i.name
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE m.id = 'LA' AND m.type = 'country'
ORDER BY i.name;
```

**预期：** 100+ 行。

## 联合国会员国

```sql
SELECT code, name
FROM countries
WHERE un_member = true
ORDER BY name;
```

**预期：** 192+ 行。

## 扁平 memberships 表（北约）

不必 `UNNEST(includes)`：

```sql
SELECT country_code, status
FROM memberships
WHERE intblock_id = 'NATO' AND status = 'member'
ORDER BY country_code;
```

**预期：** 32 行。

## 俄罗斯的前成员身份

```sql
SELECT i.id, i.name, m.status, m.joined, m.left AS departed
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE m.id = 'RU'
  AND m.type = 'country'
  AND m.status = 'former_member'
ORDER BY i.id;
```

**预期：** 11 行。`left` 在 DuckDB / Parquet / `memberships` 中均已导出。

## 按世界银行区域过滤（用 `region.id`）

```sql
SELECT code, name
FROM countries
WHERE region.id = 'ECS'
  AND code_status = 'official_iso3166_1'
ORDER BY name;
```

**预期：** 61 行。不要过滤 `region.value = 'Europe & Central Asia'`（会得到 0 行）。

## 相关文档

- [docs/agents/zh/query.md](agents/zh/query.md) — 中文查询工作流
- [llms.zh.txt](../llms.zh.txt) — 紧凑中文索引
- [AGENTS.zh.md](../AGENTS.zh.md) — 中文智能体入口

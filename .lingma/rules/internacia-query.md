# Internacia 数据查询规则

适用场景：用户询问某国信息、组织成员、陆地邻国、ISO 代码、中文国名关联等。

完整指南见 [docs/agents/zh/query.md](../../docs/agents/zh/query.md)。

## 查询方式

1. 使用 `data/datasets/internacia.duckdb`（或 Parquet），**不要** 读取 `data/countries/*.yaml`。
2. 版本：`SELECT dataset, version, schema_hash FROM _meta;`
3. 中文国名：查 `other_names`（`id = 'zh'`），例如：

```sql
SELECT c.code, oname.name
FROM countries c, UNNEST(c.other_names) AS t(oname)
WHERE oname.id = 'zh' AND oname.name = '中华人民共和国';
```

4. 组织成员（如北约/NATO）：

```sql
SELECT m.id, m.name FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE i.id = 'NATO' AND m.type = 'country';
```

5. 正式 ISO 国家（249 条）：`WHERE code_status = 'official_iso3166_1'`

更多已验证 SQL：[docs/query-examples.zh.md](../../docs/query-examples.zh.md)

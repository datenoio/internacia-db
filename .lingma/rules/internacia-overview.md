# Internacia 全局规则

本仓库是 **国家与国际组织参考数据集**（YAML 源 + DuckDB/Parquet 导出）。

## 必须遵守

1. **禁止** 向 `data/countries/` 添加 HDI、GDP、政体、互联网普及率等社会经济画像字段。
2. **禁止** 手改 `data/datasets/`（由 `python scripts/builder.py build` 生成）。
3. 查询/关联时优先使用 `data/datasets/internacia.duckdb`，不要解析源 YAML（除非在编辑数据）。
4. intblock 成员关联使用 `includes[].id`（国家 alpha-2），**不要** 使用 `includes[].name`。
5. 国家陆地边界 `borders` 存储 ISO **alpha-3** 代码，关联时用 `iso3code`。

## 详细指南

请阅读 [AGENTS.zh.md](../../AGENTS.zh.md) 与 [docs/agents/zh/query.md](../../docs/agents/zh/query.md)。

## 校验命令

```bash
python scripts/validate_countries.py --json
python scripts/validate_intblocks.py --json
pytest tests/
```

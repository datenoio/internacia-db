# Kimi Code — Internacia 补充说明

完整中文指南：[AGENTS.zh.md](../AGENTS.zh.md)  
English: [AGENTS.md](../AGENTS.md)

## 长任务（K3）建议

1. 先读 [llms.zh.txt](../llms.zh.txt)（紧凑索引），再按需打开 `docs/agents/zh/query.md`。
2. **查询** 用 DuckDB（`data/datasets/internacia.duckdb`），不要逐个解析 1300+ 个 YAML 源文件。
3. **编辑** YAML 前读 [docs/agents/zh/contribute.md](../docs/agents/zh/contribute.md)，完成后运行：

```bash
python scripts/validate_countries.py --json
python scripts/validate_intblocks.py --json
```

## 硬性护栏

- **禁止** 给 countries 添加 HDI、GDP、政体等社会经济字段。
- intblock 成员关联用 `includes[].id`，不用 `includes[].name`。
- `borders` 为 alpha-3；关联时用 `iso3code`。
- 不要手改 `data/datasets/`。

## 中文查询示例

见 [docs/query-examples.zh.md](../docs/query-examples.zh.md)。

# 智能体指南：贡献 Internacia 数据

面向 Kimi K3、GLM-5.2、通义灵码等中文 LLM 的 YAML 安全编辑流程。
English: [../contribute.md](../contribute.md)

## 编辑前必读

1. 读 [CONTRIBUTING.md](../../../CONTRIBUTING.md) 与 [country-code-policy.md](../../country-code-policy.md)（英文）。
2. **仅查询** 导出数据时用 [ai-consumers.md](../../ai-consumers.md)，不要解析 YAML。
3. **范围护栏：** countries 仅为参考数据 — **不要** 添加 HDI、GDP、政体、互联网普及率等字段。

## 源文件布局

| 路径 | 规则 |
|------|------|
| `data/countries/{CODE}.yaml` | 一实体一文件；文件名 = ISO alpha-2 `code` |
| `data/intblocks/{category}/{ID}.yaml` | 文件名必须与 `id` 完全一致（大写官方缩写；目录 = 主 `blocktype`） |
| `data/blocktypes/blocktypes.yaml` | 所有 intblock 的 `blocktype` 必须在此登记 |
| `data/datasets/` | **仅构建生成** — 禁止手改 |

## Countries 检查清单

- 必填：`code`, `name`, `iso3code`, `numeric_code`, `entity_type`, `code_status`
- 非 ISO code：需明确 `code_status`（`user_assigned`、`obsolete`）及 `recognition_status`
- `population`/`area`/`gini`：结构体 `{value, year, source, source_id}` — 未知年份用 `null`，**禁止 `year: 0`**
- `borders`：**alpha-3** 邻国代码（如 `CAN`、`MEX`），非 alpha-2
- 富化字段需添加 `provenance`（建议每条记录至少 4 条；不足时校验器会报 `INSUFFICIENT_PROVENANCE`，阈值见 `data/schemas/*_completeness.yaml`）
- 挪威代码 `'NO'`、挪威语 `'no'` 在 YAML 中须加引号，否则被解析为布尔值

## Intblocks 检查清单

- 必填：`id`, `name`, `blocktype`, `status`
- `id` 为大写 ASCII 官方缩写（规则见 [intblock-inclusion-policy.md](../../intblock-inclusion-policy.md)）
- `includes[].id` 为关联权威字段（国家 alpha-2）；`name` 仅展示
- `includes[].status` 必须是 `data/schemas/includes_status.yaml` 中的键
- 无 `includes` 且确实无成员制：设 `membership_applicability: not_applicable`
- `headquarters.country` 必须对应 `data/countries/{code}.yaml`
- `wikidata_id` 全局唯一；有意共用的 Q 号写入 `wikidata_duplicate_allowlist`
- 主题键必须存在于 `data/schemas/topics.yaml`
- `partof` / `predecessor` / `successor` / `suborganizations[].id` 必须能解析到已有 intblock
- 已解散组织：`status: historical` + `dissolved` 日期；不要编造成员列表
- `last_verified`：对照官方名录核对当天的 `YYYY-MM-DD`（12 个月顾问 SLA）
- 新 blocktype 须先加入 `data/blocktypes/blocktypes.yaml`
- 完整逐步示例：[add-intblock-example.md](../add-intblock-example.md)`

## 提交 PR 前校验

```bash
python scripts/validate_countries.py --json   # 退出码 0 = 无错误；1 = 有错误（警告默认不失败）
python scripts/validate_intblocks.py --json
pytest tests/
ruff check internacia_builder/ scripts/ tests/
python scripts/builder.py build --formats parquet,duckdb
```

## Schema 或破坏性变更

须先 OpenSpec 提案 — 见 [openspec-quickstart.md](../openspec-quickstart.md)。**批准前不要实现。**

## 常见修复

| 问题 | 修复 |
|------|------|
| borders 用了 alpha-2 | 改为 alpha-3 |
| population 写成 plain number | 改为 `{value, source, ...}` 结构体 |
| 缺少 includes | 填充 includes 或设 `membership_applicability: not_applicable` |
| 无效 blocktype | 加入 `blocktypes.yaml` 后重新校验 |

## 相关

- [AGENTS.zh.md](../../../AGENTS.zh.md)
- [query.md](query.md)
- [add-intblock-example.md](../add-intblock-example.md) — 新增 intblock 示例（英文）
- `.agent/workflows/edit-intblock.md`

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
| `data/intblocks/{category}/{ID}.yaml` | 文件名必须与 `id` 完全一致（大写官方缩写；目录 = `blocktype` 列表的第一个值） |
| `data/blocktypes/blocktypes.yaml` | 所有 intblock 的 `blocktype` 必须在此登记；选择目录前请阅读各键的 `description` |
| `data/datasets/` | **仅构建生成** — 禁止手改 |

## Countries 检查清单

- 必填：`code`, `name`, `iso3code`, `numeric_code`, `entity_type`, `code_status`
- 非 ISO code：需明确 `code_status`（`user_assigned`、`obsolete`）及 `recognition_status`
- `population`/`area`/`gini`：结构体 `{value, year, source, source_id}` — 源 YAML 中未知年份省略 `year`，导出数据中用 `null`，**禁止 `year: 0`**
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
- 新 blocktype 须先加入 `data/blocktypes/blocktypes.yaml`，并附 `description`；blocktype 表示领域，不表示实体形式
- 不要使用已弃用的 `intorg`；实体形式请用 `scope_category`（IGO 用 `scope_category = 'igo'` 过滤）
- 完整逐步示例：[add-intblock-example.md](../add-intblock-example.md)

## 提交 PR 前校验

```bash
python scripts/validate_countries.py --json   # 退出码 0 = 无错误；1 = 有错误（警告默认不失败）
python scripts/validate_intblocks.py --json
python scripts/builder.py build             # 重新生成全部格式
python scripts/check_generated_artifacts.py
pytest tests/
ruff check internacia_builder/ scripts/ tests/
python scripts/generate_data_dictionary.py --check
python scripts/check_doc_counts.py
python scripts/check_markdown_links.py
```

构建清单（`*.manifest.json`）、`datapackage.json` 及二进制/批量导出都是构建产物，git 忽略它们，
因此数据变更通常不会改动 `data/datasets/`。仅当构建改动了仍被 git 跟踪的描述文件
（`contract.json`、数据集卡片、别名 JSON、`border_status.json`）时才提交它们；禁止手改导出文件。
部分格式构建不会更新 JSONL/YAML，不能替代完整构建。文档中的 intblock 数量按百位向下取整
（`1300+`），仅在 `scripts/check_doc_counts.py` 报告新的百位时更新。新增或删除记录时，
同步更新受影响的查询预期结果。CI 先检查已提交的描述文件，再构建 `.ci-datasets` 并对该目录运行测试。

面向使用者的变更请新增 `changelog.d/<slug>.md` 片段，不要直接编辑 `CHANGELOG.md`，
也不要写 "(1304 intblocks)" 这类累计数量。见 [changelog.d/README.md](../../../changelog.d/README.md)。

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
- [discover.md](../discover.md) — 查找缺失记录 / 改进已有 YAML（英文）
- [discovery.md](../../discovery.md) — 检索与改进方法（英文）
- [intblock-inclusion-policy.md](../../intblock-inclusion-policy.md) — 收录规则（英文）
- [intblock-sources.md](../../intblock-sources.md) — 已检索的目录与成员名录来源（英文）
- `.agent/workflows/edit-intblock.md`

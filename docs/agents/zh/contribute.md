# 智能体指南：贡献 Internacia 数据

面向 Kimi K3、GLM-5.2、通义灵码等中文 LLM 的国家、intblock 与贸易协定 YAML 安全编辑流程。
English: [../contribute.md](../contribute.md)

## 编辑前必读

1. 读 [CONTRIBUTING.md](../../../CONTRIBUTING.md) 与 [country-code-policy.md](../../country-code-policy.md)（英文）。
2. **仅查询** 导出数据时用 [ai-consumers.md](../../ai-consumers.md)，不要解析 YAML。
3. **范围护栏：** countries 仅为参考数据 — **不要** 添加 HDI、GDP、政体、互联网普及率等字段。

## 源文件布局

| 路径 | 规则 |
|------|------|
| `data/countries/{CODE}.yaml` | 一实体一文件；文件名 = ISO alpha-2 `code` |
| `data/intblocks/{category}/{ID}.yaml` | 文件名必须与 `id` 完全一致（大写官方缩写；目录 = `blocktype` 列表的第一个值）；`id` 全局唯一 |
| `data/blocktypes/blocktypes.yaml` | 所有 intblock 的 `blocktype` 必须在此登记；选择目录前请阅读各键的 `description` |
| `data/trade_agreements/{ID}.yaml` | 贸易协定注册表；文件名必须与 `id` 一致；id 与 intblock id 及别名共用一个命名空间。规则见 [CONTRIBUTING.md](../../../CONTRIBUTING.md#trade-agreements-registry)（英文） |
| `data/borders/border_status.yaml` | 关闭或受限的陆地边界。规则见 [CONTRIBUTING.md](../../../CONTRIBUTING.md#border-status)（英文） |
| `data/datasets/` | **仅构建生成** — 禁止手改 |

## Countries 检查清单

- 必填：`code`, `name`, `iso3code`, `numeric_code`, `entity_type`, `code_status`
- 非 ISO code（`user_assigned`、`obsolete`）：在 [country-code-policy.md](../../country-code-policy.md) 中记录；需要时添加 `recognition_status`
- `population`/`area`/`gini`：结构体 `{value, year, source, source_id}` — 源 YAML 中未知年份省略 `year`，导出数据中用 `null`，**禁止 `year: 0`**；数值必须合理（人口不能为负，gini 在 0–100 之间，不能是未来年份）
- `borders`：**alpha-3** 邻国代码（如 `CAN`、`MEX`），非 alpha-2；每个都必须能解析到已有国家的 `iso3code`，且应当互为邻国（对方也列出你）— 例外写入 `countries_completeness.yaml` 的 `borders.reciprocity_allowlist`
- 附属领地、特别行政区和统计区域不得设 `un_member`/`independent` 为 `true`
- `tld` 为 `.xx` 形式的小写；`calling_codes` 为 `+数字`；`timezones` 必须是 IANA 时区名；`flag_emoji` 必须与该 code 的区域指示符对一致；`landlocked: true` 要求 `borders` 非空
- `capital_city` 坐标必须合理：分析器会标记距 `centroid` 超过按面积缩放距离的首都（`CAPITAL_FAR_FROM_CENTROID`）— 通常意味着经纬度写反；合理的例外写入 `geography.capital_distance.allowlist`
- `subregion` 必须属于该记录 `continents` 之一；跨洲例外写入 `countries_completeness.yaml` 的 `region_hierarchy.allowlist`
- 富化字段需添加 `provenance`（建议每条记录至少 4 条；不足时校验器会报 `INSUFFICIENT_PROVENANCE`，阈值 `provenance.min_count` 见 `data/schemas/*_completeness.yaml`）
- 用 `python scripts/enrich_countries.py` 刷新（见 [enrichment.md](../../enrichment.md)，英文）
- 挪威代码 `'NO'`、挪威语 `'no'` 在 YAML 中须加引号，否则被解析为布尔值

## Intblocks 检查清单

- 必填：`id`, `name`, `blocktype`, `status`
- `id` 为大写 ASCII 官方缩写（规则见 [intblock-inclusion-policy.md](../../intblock-inclusion-policy.md)）
- `includes[].id` 为关联权威字段（国家 alpha-2）；`name` 仅展示
- `includes[].status` 必须是 `data/schemas/includes_status.yaml` 中的键
- 无 `includes` 且确实无成员制：设 `membership_applicability: not_applicable`
- 完整度优先级见 `data/schemas/intblocks_completeness.yaml`（高：includes；中：wikidata_id、非模板化 description；低：languages、headquarters、regions、other_names、provenance、links）。`provenance` 应至少列出 4 条字段级条目（`min_count: 4`；不足时报 `INSUFFICIENT_PROVENANCE`）
- 已解散组织：`status: historical` + `dissolved` 日期；不要编造成员列表。`founded`/`dissolved` 必须是真实日期（`YYYY`、`YYYY-MM`、`YYYY-MM-DD` 或 `YYYYs`）— **禁止 `YYYY-00-00`** — 且 `dissolved` 不得早于 `founded`
- `partof` / `predecessor` / `successor` / `suborganizations[].id` 必须能解析到已有 intblock `id` 或别名；没有独立记录的附属机构写入 `intblocks_completeness.yaml` 的 `references.org_ref_allowlist`
- `headquarters.country` 必须对应 `data/countries/{code}.yaml`
- `wikidata_id` 全局唯一；有意共用的概念 Q 号写入 `references.wikidata_duplicate_allowlist`，并附注释说明原因
- 设置了 `membership_count` 时，应与 `includes` 数量（全部条目或成员类条目）一致
- `includes[].joined`/`left` 必须是真实日期，`left` 不得早于 `joined`，二者都不得晚于 `dissolved`（早于 `founded` 加入是允许的 — 批准先于生效）
- `founding_members` 条目必须能解析到国家 code 且出现在 `includes` 中（已退出的创始成员用 `former_member`）
- 历史实体国家（如 `AN`、`SU`）在非历史组织中不得带有效成员状态 — 用 `former_member`
- 主题键必须存在于 `data/schemas/topics.yaml`；确属新增的键在同一个 PR 中加入该目录
- 在 `provenance` 中引用官方成员名录（检索与改进方法见 [discovery.md](../../discovery.md)；已检索目录与名录来源见 [intblock-sources.md](../../intblock-sources.md)）
- 沿革：`predecessor`/`successor` 指向的记录若反向字段为空，须补上反向引用；出现在上级 `suborganizations` 中的记录必须在 `partof` 中声明该上级
- 同一 blocktype 下的记录共用英文缩写会报 `DUPLICATE_ACRONYM`；现实中确实重名的写入 `references.acronym_duplicate_allowlist`
- `last_verified`：对照 `provenance` 中的来源核对记录的日期；新增或修改的 intblock 必须有，修改 `includes` 时必须更新（Tier-1 组织 6 个月后过期，其余 12 个月；见 CONTRIBUTING.md）
- 新 blocktype 须先加入 `data/blocktypes/blocktypes.yaml`，并附 `description`；blocktype 表示领域，不表示实体形式
- 不要使用已弃用的 `intorg`；实体形式请用 `scope_category`（IGO 用 `scope_category = 'igo'` 过滤；见 [blocktype semantics](../../intblock-inclusion-policy.md#blocktype-semantics)）
- 不要使用已弃用的复合 blocktype `eccurr` 与 `cuscurr`；改为列出 `economic` 或 `customs` 加 `currency`。货币联盟单独建一条 `currency/` 记录
- 完整逐步示例：[add-intblock-example.md](../add-intblock-example.md)

## 提交 PR 前校验

```bash
python scripts/validate_countries.py --fail-on-warning
python scripts/validate_intblocks.py --fail-on-warning
python scripts/validate_countries.py --json   # 智能体结构化输出；退出码 0 = 无错误，1 = 有错误
python scripts/validate_intblocks.py --json
# --fail-on-warning：警告也会失败（退出码 1），与 CI 相同。基于日期的过期警告
# （last_verified 与 provenance 时效）只报告，不会导致失败。
python scripts/builder.py build             # 重新生成全部格式
# INTERNACIA_ZSTD_LEVEL=3 python scripts/builder.py build  # 快近 2 倍；CI 用此设置，发布用 22
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
部分构建不会刷新全部描述文件，不能替代完整构建。文档中的 intblock 数量按百位向下取整
（例如 1304 条记录写作 `1300+`），仅在 `scripts/check_doc_counts.py` 报告新的百位时更新。
新增或删除记录时，同步更新受影响的查询示例预期结果。

CI 重新构建到 `.ci-datasets`，用它检查已提交的描述文件，检查第二次构建结果完全相同，
并对该暂存目录运行测试（`.github/workflows/validate.yml`）。

面向使用者的每项变更（新增或退役记录、成员名录修复、schema 或语义变更）都要新增
`changelog.d/<slug>.md` 片段，使用 Keep a Changelog 小节；不要直接编辑 `CHANGELOG.md`，
也不要写 "(1304 intblocks)" 这类累计数量。见 [changelog.d/README.md](../../../changelog.d/README.md)。

## Schema 或破坏性变更

新能力、schema 变更或破坏性导出须先提交 OpenSpec 提案：

1. 读 [openspec-quickstart.md](../openspec-quickstart.md) 或完整的 [openspec/AGENTS.md](../../../openspec/AGENTS.md)
2. 创建 `openspec/changes/<change-id>/`，含 `proposal.md`、`tasks.md` 与 spec 增量
3. 运行 `openspec validate <change-id> --strict`
4. **批准前不要实现。**

## 常见修复

| 问题 | 修复 |
|------|------|
| borders 用了 alpha-2 | 改为 alpha-3（邻国的 `iso3code`） |
| population 写成 plain number | 改为 `{value, source, ...}` 结构体 |
| intblock id 冲突 | 另选唯一 `id`；`intblocks_aliases` 中的别名只能通过维护者流程添加 |
| 缺少 includes | 填充 includes 或设 `membership_applicability: not_applicable` |
| 无效 blocktype | 加入 `blocktypes.yaml` 后重新校验 |
| 富化字段缺少 provenance | 在 `provenance` 列表中追加 `{field, source, retrieved_at}` |

## 相关

- [AGENTS.zh.md](../../../AGENTS.zh.md)
- [AGENTS.md](../../../AGENTS.md) — 英文路由入口
- [query.md](query.md)
- [add-intblock-example.md](../add-intblock-example.md) — 新增 intblock 示例（英文）
- [discover.md](../discover.md) — 查找缺失记录 / 改进已有 YAML（英文）
- [discovery.md](../../discovery.md) — 检索与改进方法（英文）
- [intblock-inclusion-policy.md](../../intblock-inclusion-policy.md) — 收录规则（英文）
- [intblock-sources.md](../../intblock-sources.md) — 已检索的目录与成员名录来源（英文）
- `.agent/workflows/edit-intblock.md`

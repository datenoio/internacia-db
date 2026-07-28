# Internacia 数据编辑规则

编辑 `data/countries/`、`data/intblocks/` 或 `data/blocktypes/` 时生效。

完整清单见 [docs/agents/zh/contribute.md](../../docs/agents/zh/contribute.md)。

## 核心规则

- 文件名必须与记录 id 完全一致（intblock 区分大小写，如 `UfM.yaml`）。
- `borders` 使用 **alpha-3**（如 `CAN`、`MEX`），不是 alpha-2。
- `population`/`area`/`gini` 为结构体；未知年份用 `null`，禁止 `year: 0`。
- 无成员列表的 intblock 须设 `membership_applicability: not_applicable`。
- YAML 中挪威 `'NO'`、挪威语 `'no'` 必须加引号。
- 富化字段须添加 `provenance` 条目。
- 新 blocktype 须先写入 `data/blocktypes/blocktypes.yaml`。

## 编辑后必跑

```bash
python scripts/validate_countries.py --json
python scripts/validate_intblocks.py --json
```

根据 JSON 输出中的 `errors` 与 `fix_hint` 修复问题。Schema 或破坏性变更须先 OpenSpec 提案。

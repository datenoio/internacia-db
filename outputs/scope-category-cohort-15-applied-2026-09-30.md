# Применение 15 категорий intblocks (30 сентября 2026)

> **Исторический срез:** этот отчёт описывает промежуточное состояние с четырьмя предупреждениями. Все четыре случая исправлены позже в тот же день; актуальные числа и проверки — в [финальном отчёте](final-four-applied-2026-09-30.md).

Изменение выполнено в worktree `manus/crosswalk-wb-remediation`. Расширены source JSON Schema, общий validator/quality rule, OpenAI lookup enum и потребительская документация. В `data/schemas/scope_category_model_gap.yaml` записаны 15 точных assignments с официальными источниками и датой обращения; `scripts/backfill_scope_category.py --manifest data/schemas/scope_category_model_gap.yaml --apply` применил все 15, повторный `--check` показал **0 pending / 0 conflicts**. Источники и категории подтверждены в `provenance` каждой записи.

| Категория | Число | ID |
|---|---:|---|
| `intergovernmental_body` | 12 | APFIC, CECAF, CIFAA, CODEX, COPESCAALC, EIFAAC, SWIOFC, WECAFC, ADF, AF, RDR, GCCPO |
| `non_state_organization` | 3 | MSF, CANTO, ACIL |

**Исправление ложных membership-связей.** У ADF (26), AF (24), GCCPO (6), MSF (41), CANTO (44) и ACIL (22) удалены все неподтверждённые/неприменимые к ним country `includes` и `membership_count`; source YAML содержит `membership_applicability: not_applicable`. У GCCPO также удалено ложное `founding_members`. Для ACIL исправлены описание и классификация как NGO, для MSF/CANTO и двух фондов пояснена роль прежних стран. У RDR удалены BE и IT (участвующие субнациональные юрисдикции, не государства-члены Совета) и LU (консультативный представитель), а DE, AT, CH и LI оставлены как `participant`, не `member`; роль удалённых единиц сохранена в notes. Итого удалено **166** элементов `includes` (163 у шести сущностей без country roster и 3 у RDR). Данные о донорах и beneficiaries не выдаются за членство; моделирование их как отдельных типизированных временных связей потребует отдельного изменения схемы.

**Нюанс экспорта:** `membership_applicability` — source-only marker; в DuckDB отсутствие `includes` экспортируется как `NULL`, а не пустой список. Для поиска зависимых органов без country roster использовать `COALESCE(len(includes), 0) = 0` (проверенный пример в `docs/query-examples.md`). Категория сущности сама по себе не доказывает существование country-member roster.

## Проверка

- После пересборки: **256 countries, 1278 intblocks, 78 blocktypes, 59 650 membership rows**; source/Parquet/DuckDB согласованы.
- `validate_countries.py --json`: **0 ошибок, 0 предупреждений**. `validate_intblocks.py --json`: **0 ошибок, 4 предупреждения**. Свежий quality analyzer подтверждает те же четыре `MISSING_SCOPE_CATEGORY`.
- Полный `pytest -q`, Ruff на изменённом Python-коде, `check_generated_artifacts.py`, `check_doc_counts.py`, `openspec validate complete-intblock-scope-taxonomy --strict` и `git diff --check` прошли.
- Повторные dry-run/check: 15 категорий уже назначены, очистка roster **идемпотентна** (0 файлов к изменению). Integration tests проверяют 15 категорий, provenance, отсутствие membership edges у шести записей и четыре `participant` у RDR.

## Осталось отдельно

С **19 до 4** сократилось число предупреждений по formal-записям: **AFDF, CIF, TAR, TELESUR**. Не присваивать им новую категорию автоматически. AFDF требует исправления 82-country roster до официальных 29 State Participants и существующей категории `igo`; CIF требует решения, разделять ли финансовую архитектуру и датированный список доноров; TAR смешивает 22 стороны договора и 28 стран сети; TELESUR — национальная коммерческая компания, требующая решения об исключении из membership-oriented intblocks. До урегулирования этих четырёх случаев отсутствие категории остаётся **warning**, не error.

Вне задачи по категориям отмечены отдельные остаточные вопросы качества содержания: у CODEX полный официальный состав — 188 государств + EU, но `includes` содержит только EU; у COPESCAALC действующее наименование COPPESAALC и в специализированном FAO roster есть Nicaragua как 21-й участник. Они не были молча «исправлены» без отдельной roster-миграции. Подробное юридическое обоснование и первичные ссылки см. в [анализе исходных 19 случаев](remaining-scope-category-options-2026-09-30.md) и в `data/schemas/scope_category_model_gap.yaml`.

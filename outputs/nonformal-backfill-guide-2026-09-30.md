# Подготовленный backfill для 30 non-formal записей

**Актуальный статус на 30 сентября 2026 года:** шесть индивидуально утверждённых категорий уже применены; массовый `--apply` для всех 30 **по-прежнему заблокирован**. Из 30 строк [аудита](nonformal-scope-audit-2026-09-30.csv) 18 имеют `source_reviewed` (12 первоначальных и шесть применённых), а 12 остаются на `pending_review`. Для 10 из 12 предложен пересмотр самой записи, ещё для двух (`PALOP`, `SOUTHERNCONE`) — сначала уточнение состава. Подробности и оговорки: [индивидуальный разбор](individual-nonformal-scope-decisions-2026-09-30.md).

Рабочие файлы: [CLI](../scripts/backfill_nonformal_scope_category.py) и [curated manifest](../data/schemas/scope_category_nonformal_30.yaml). Manifest фиксирует для каждого ID ожидаемые `status`, категорию, точный путь и SHA-256 **исходного** YAML. У 18 проверенных решений есть индивидуальное `evidence`, в том числе у шести уже применённых; остальные 12 строк всё ещё представляют предварительные предложения, а не разрешение на правку. Оригинальный SHA-256 у уже применённых строк сохраняется как baseline перед добавлением поля: идемпотентность скрипт проверяет по значению и provenance.

## Проверка без записи

В worktree `/Users/ibegtin/workspace/commondataio/internacia-db-crosswalk-wb` доступно проектное виртуальное окружение исходного checkout:

```bash
cd /Users/ibegtin/workspace/commondataio/internacia-db-crosswalk-wb
export PYTHONPATH="$PWD/scripts:$PWD"
PY=/Users/ibegtin/workspace/commondataio/internacia-db/.venv/bin/python
$PY scripts/backfill_nonformal_scope_category.py \
  --report-json .work/nonformal78/nonformal-30-dry-run.json
```

Актуальная сводка: `assignments=30 ready=18 blocked=12 conflicts=0 pending=12 already_set=6 applied=0`. JSON-отчёт содержит ID и причину блокировки каждого случая. `--check` до разрешения 12 спорных записей завершится кодом `1`; это ожидаемое поведение, а не ошибка входных данных.

Не разблокируйте оставшиеся 12 механической заменой `pending_review`: в десяти случаях нужна проверка пригодности записи для реестра, а в двух — выбор границы состава. Если применимое решение будет принято, добавьте **собственный для записи** HTTPS-источник (`source`, `url`, `retrieved_at`) и только тогда обновите review state. Если исходный YAML изменился до применения, сценарий обнаружит расхождение SHA-256; проверяйте изменения до обновления fingerprint. Шесть уже применённых категорий не изменили сомнительные `includes[].status` у справочных наборов — это отдельная задача.

## После review и согласования изменения

```bash
$PY scripts/backfill_nonformal_scope_category.py --report-json .work/nonformal78/approved-dry-run.json
# Продолжать лишь при ready=30, blocked=0, conflicts=0.
$PY scripts/backfill_nonformal_scope_category.py --apply \
  --report-json .work/nonformal78/applied.json
$PY scripts/backfill_nonformal_scope_category.py --check
$PY scripts/builder.py build
$PY scripts/validate_intblocks.py --json
$PY scripts/check_generated_artifacts.py
$PY -m pytest -q tests/test_backfill_nonformal_scope_category.py
```

Повторный `--apply` после полного согласования идемпотентен. Скрипт меняет только `scope_category` и его field-level provenance, **не исправляет** сомнительные `includes[].status`, списки сторон договоров или динамические наборы виз. Полная проверка исходников проводится **до** первой записи, но массовое сохранение файлов не является транзакцией на уровне файловой системы: выполнять его в Git worktree с доступным откатом. Сейчас остаются **72** непромаркированные non-formal записи из исходных 78; число 48 достижимо только если впоследствии будут утверждены и применены **все** 30 предложений, чего текущий пообъектный анализ не рекомендует. `validate_intblocks.py` пока не считает non-formal пропуски ошибками.

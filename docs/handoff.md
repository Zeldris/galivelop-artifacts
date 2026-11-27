<!-- galivelop-workflow v0.9.1 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `ccr-c6c4e060-0l41l0` (sesión en la nube; sale de `claude/arranque`) |
| **Fase / tarea** | gart-H2 implementado (`gart/schema.py` + `tests/test_schema.py`, base gvoice@1990d92 recortada a las 18 palabras clave del DDD §6, con `enum` no vacío y orden estable de oi); falta la revisión del bloque y cerrar la tarea. Presupuesto de compactaciones: 0 |
| **Último punto estable** | el commit de gart-H2 (validador del subconjunto de JSON Schema) |
| **Siguiente paso** | revisión del bloque con `/code-review` (diff desde el último `Findings:`) y cerrar gart-H2; después gart-H3 (apuntado: `allOf`, `if/then/else`, `maxProperties`, `dependentRequired`); a `main` solo con confirmación y las tres fases |
| **Check** | verde tras gart-H2 (unittest, doctor sin FAIL, ci-local) |

## Para la próxima publicación

_(lo que va a `main` a continuación, y a qué espera)_

## Hecho (5 últimas)

1. 2026-11-27 — gart-H2: `gart/schema.py` (`SchemaError`, `ValidationError`, `check_schema`, `validate`), portado de gvoice; 56 tests.
2. 2026-11-27 — CI de GitHub arranca otra vez (verde en f45a1ce); quitado de pendientes.
3. 2026-11-27 — Flujo a v0.9.1 (`/gw-update`): 110 archivos del flujo, `gw.json`, 2 reglas nuevas en `REVIEW.md`, marcadores.
4. 2026-11-27 — gart-H1: `KindId` (análisis, validación, `/0` provisional, `next()`), inv. 1 con tabla de válidos e inválidos.

## Pendiente

Lo pendiente está en [`docs/records/pending.md`](records/pending.md); se añade y se quita allí.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `bash -n .githooks/pre-commit`, `bash -n .githooks/pre-push`, `python3 -m unittest discover -s tests -t .`, `python3 .claude/gw/scripts/doctor.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.

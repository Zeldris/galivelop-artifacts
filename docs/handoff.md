<!-- galivelop-workflow v0.9.1 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `ccr-c6c4e060-0l41l0` (sesión en la nube; sale de `claude/arranque`) |
| **Fase / tarea** | gw-update 0.9.0→0.9.1 hecho (Q-9..Q-12 respondidas: en esta rama, `--update`, reglas nuevas de `REVIEW.md` a mano). gart-H2 empezado: 3 de las 4 copias clonadas en solo lectura (gimg, gvoice, oi), un Explore haiku las compara; `galivelop-developer` rechazado por el permiso automático (Q-13 abierta). Presupuesto de compactaciones: 0 |
| **Último punto estable** | el commit de la 0.9.1 |
| **Siguiente paso** | gart-H2: respuesta a Q-13 (gdev); si el resumen del Explore se perdió, repetirlo sobre los clones (`/home/user/zeldris/galivelop-{image,voice}-generator`, `/home/user/galivelop-client-catcher`, se reclonan con `git clone --depth 1`); luego un `gw-worker` `sonnet` migra el validador y sus tests; a `main` solo con confirmación y las tres fases |
| **Check** | verde tras la 0.9.1 (unittest, doctor sin FAIL, `apply.py --check` en 0, ci-local) |

## Para la próxima publicación

_(lo que va a `main` a continuación, y a qué espera)_

## Hecho (5 últimas)

1. 2026-11-27 — Flujo a v0.9.1 (`/gw-update`): 110 archivos del flujo, `gw.json`, 2 reglas nuevas en `REVIEW.md`, marcadores.
2. 2026-11-27 — gart-H1: `KindId` (análisis, validación, `/0` provisional, `next()`), inv. 1 con tabla de válidos e inválidos.

## Pendiente

Lo pendiente está en [`docs/records/pending.md`](records/pending.md); se añade y se quita allí.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `bash -n .githooks/pre-commit`, `bash -n .githooks/pre-push`, `python3 -m unittest discover -s tests -t .`, `python3 .claude/gw/scripts/doctor.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.

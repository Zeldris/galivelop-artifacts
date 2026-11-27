<!-- galivelop-workflow v0.9.0 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `claude/arranque` |
| **Fase / tarea** | DDD final en `docs/records/ddd-galivelop-artifacts.md`, desde `../galivelop-developer/docs/records/` (`ddd-galivelop-artifacts-borrador2.md` y `revision-ddd-gart-borrador2.md`, solo lectura). Preguntas q7–q14 hechas (`docs/questions.md`), sin contestar. Presupuesto de compactaciones: 0 |
| **Último punto estable** | las preguntas registradas; el DDD sigue siendo el borrador 1 |
| **Siguiente paso** | con las respuestas, escribir el DDD: q1–q6 y ADR 0001–0006 se conservan; q7 en adelante, un ADR cada una; aplicar R1–R10 y Q-177 a Q-179 (respuesta «a»); hitos `gart-H<n>` |
| **Check** | `bash -n .githooks/pre-commit`, `bash -n .githooks/pre-push`, `python3 -m unittest discover -s tests -t .`, `python3 .claude/gw/scripts/doctor.py`, `python3 .claude/gw/scripts/ci-local.py --validate`: verde (árbol `cbc403d`) |

## Para la próxima publicación

_(lo que va a `main` a continuación, y a qué espera)_

## Hecho (5 últimas)

1. _(fecha — qué se cerró, en dos líneas como mucho: el detalle está en el commit; la más antigua sale cuando hay más
   de 5, el historial está en git)_

## Pendiente

Lo pendiente está en el archivo de `pendingFile` (`.claude/gw.json`; por defecto `docs/records/pending.md`): decisiones de la persona que bloquean algo, problemas conocidos, ideas sin planificar. Se añade y se quita allí; `handoff.py move-pending` rehace esta línea y `handoff.py add-pending "texto"` añade sin leer el archivo.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `bash -n .githooks/pre-commit`, `bash -n .githooks/pre-push`, `python3 -m unittest discover -s tests -t .`, `python3 .claude/gw/scripts/doctor.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.

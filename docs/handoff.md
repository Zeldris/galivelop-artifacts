<!-- galivelop-workflow v0.9.1 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `ccr-5bf1928c-gjj56w` (sesión en la nube; sale de `main` tras fusionar PR #1) |
| **Fase / tarea** | gart-H3 en curso. Hecho: `gart.diff/0` (32 filas), palabras clave de gimg y gvoice (Q-18 a), revisión del bloque, `tools/copies_tests.py` y su resultado en `docs/records/gart-H3-tests.md`: gdev y gimg pasan enteras contra gart; gvoice falla 331 por `$ref` externos (D29, gart-H4); oi 37 por forma (D31, D32). Clones en solo lectura: `/home/user/galivelop-developer`, `/home/user/galivelop-client-catcher`, `/home/user/zeldris/galivelop-image-generator`, `/home/user/zeldris/galivelop-voice-generator`. Presupuesto de compactaciones: 1 |
| **Último punto estable** | el commit `fix(gart-H3)` de la revisión del bloque (Findings: 3) |
| **Siguiente paso** | gart-H3: esperar Q-20 (cerrar H3 así o no) y Q-21 (`actual` en el error type); con Q-21 a, añadirlo en `gart/schema.py` con su test |
| **Check** | verde (unittest con test_copies omitido sin `GART_COPIES` y en verde con él, doctor sin FAIL, ci-local) |

## Para la próxima publicación

gart-H12 (barrido de canon.py), por pull request.

## Hecho (5 últimas)

1. 2026-11-28 — gart-H3 paso 1: tabla `gart.diff/0` (30 filas: regla, alcance, forma, pendiente), seis palabras clave de gimg y gvoice, `$ref "#"` rechazado, índices en orden numérico; `tools/copies_probe.py` para la comparación.
2. 2026-11-27 — Revisión del bloque gart-H12: `loads_strict` sin recorrido carácter a carácter (prescan de profundidad con regex, `_walk` con puntero solo al lanzar); 6 leves a pendientes.
3. 2026-11-27 — gart-H12: barrido de `gart/canon.py` (subclases de int/float, `canon.depth` con `MAX_DEPTH` 512 y ciclos, `path` JSON Pointer en `loads_strict`, motivos de los vectores, muestra RFC 8785 §3.2.2 con bytes a mano); 5 leves de gart-H9 cerrados.
4. 2026-11-27 — Fase 1 hacia `main` (diff desde 3326968): sin graves ni medios, 2 leves a pendientes; docs de la inv. 9 y ADR 0007 al día (floats ≥ 2^53).
5. 2026-11-27 — Revisión del bloque gart-H9: entero enorme y sustitutos sueltos rechazados por `loads_strict` como CanonError, motivos de test no vacíos; 4 leves apuntados.

## Pendiente

Lo pendiente está en [`docs/records/pending.md`](records/pending.md); se añade y se quita allí.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `bash -n .githooks/pre-commit`, `bash -n .githooks/pre-push`, `python3 -m unittest discover -s tests -t .`, `python3 .claude/gw/scripts/doctor.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.

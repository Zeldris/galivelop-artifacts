<!-- galivelop-workflow v0.9.1 -->
# gw-opt-tokens — notas del proyecto

Las lee la skill `gw-opt-tokens` antes de proponer nada, y se actualizan cuando la persona aprueba un cambio. El flujo
las crea una vez; desde entonces son del proyecto.

## Herramientas que ya ahorran

<!-- Una línea cada una, con cómo se corre. -->
- `python3 .claude/gw/scripts/recover.py --state` y `--search "<texto>"`: recuperar lo que se llevó una
  compactación.
- `gw-orchestrate-dealer`: el trabajo de más de un paso, repartido a subagentes de contexto limpio.

## Costes conocidos

<!-- Lo que se ha visto que cuesta mucho en este proyecto (archivos grandes leídos enteros, salidas largas...). -->
- `docs/records/ddd-galivelop-artifacts.md` (~245 líneas): se lee por secciones, `grep -n '^## '` y `sed -n` de la
  que haga falta (§7 hitos, §8 preguntas). Entero y 9 veces arrastró 874k tokens en gart-H1/H2/H9.
- Otros repos (el del flujo incluido) siempre por subagente que devuelve el resumen: un `grep` directo arrastró 576k.
- `add_repo`: si falla dos veces, se lee el motivo y se pregunta a la persona; no se reintenta a ciegas (5 de 10
  fallaron).
- Conectores sin uso (Claude Docs y otros): los apaga la persona en `/context`; el arranque fijo (~97,5k por llamada)
  es el 81 % de la entrada.

## Ajustes en vigor

- Ventana de compactación automática: `CLAUDE_CODE_AUTO_COMPACT_WINDOW` en `.claude/settings.json`.

## Referencias medidas

<!-- Cifras medidas con las que comparar: fecha, sesión, contexto medio, llamadas, total. -->
- 2026-11-27, rama `ccr-c6c4e060-0l41l0` (gart-H1, H2, H9; `--since 2eca8da`): 124 llamadas, contexto medio 119.867,
  14,9M de entrada en la principal; 9 subagentes, 74 llamadas, 3,3M; total 18,1M.

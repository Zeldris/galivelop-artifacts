# ¿Cuándo pasa un tipo de `/0` a `/1`?

<!-- gvc-ddd-decision: q13 -->

Status: accepted

Lo sube a mano el repo dueño cuando el check de otro repo depende del tipo; que GVE lo lea no cuenta.

Por qué: GVE ya lee tipos `/0`, y gart no puede saber quién usa un tipo.

Descartado: Automáticamente cuando lo usa un consumidor de otro repo.

Sección de origen: 2. Lenguaje del dominio

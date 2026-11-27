# ¿Qué entra en el hash de un artefacto?

<!-- gvc-ddd-decision: q9 -->

Status: accepted

El artefacto sin el campo de sobre `meta`, definido en `gart.common/0`.

Por qué: El hash no depende del esquema y otro lenguaje lo reproduce. Coste: 2 esquemas de gdev mueven sus campos volátiles a `meta` en un `/0`, y un `/1` estable de GVE con esos campos pediría su `/2`.

Descartado: El artefacto entero; quitar los campos anotados con `x-gart-volatile`.

Sección de origen: 2. Lenguaje del dominio, 5. Invariantes

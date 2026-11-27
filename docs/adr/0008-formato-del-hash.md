# ¿Qué formato tiene el hash?

<!-- gvc-ddd-decision: q8 -->

Status: accepted

`sha256:<hex>`, también en `file_hash` para los archivos que no son JSON.

Por qué: Permite cambiar de algoritmo sin ambigüedad.

Descartado: Hex sin prefijo.

Sección de origen: 2. Lenguaje del dominio

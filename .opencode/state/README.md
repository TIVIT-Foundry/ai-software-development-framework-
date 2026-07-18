# State Directory

Almacena el estado de sesión del framework para reanudar ejecuciones interrumpidas.

## Archivos

- `progress.json` — Estado actual de skills ejecutadas y bundle activo.

## Formato de progress.json

```json
{
  "vertical": "nombre-del-vertical",
  "bundle_actual": "bundle-scaffold",
  "skills_ejecutadas": ["framework-governance", "framework-discovery"],
  "skill_actual": "framework-scaffold-implementation",
  "ultima_modificacion": "2026-06-05T10:30:00Z"
}
```

Este directorio no contiene artefactos de diseño ni documentación, solo estado transitorio.

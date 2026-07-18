---
name: file-upload
description: "File upload and storage patterns for applications. Covers blob storage (S3, Azure Blob, GCS), upload patterns (multipart, chunked, streaming, presigned URLs), MIME validation, size limits, virus scanning, thumbnails, CDN integration, and lifecycle policies. Trigger: When implementing file upload, storage, or download functionality."
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: recommended
  depends_on:
  - backend-api
  - security
  consumed_by:
  - angular
  agent_roles:
  - delivery-agent
  validation_profile: architecture-consistency
  mcp_usage: none
---

# file-upload

## Propósito

Esta skill define cómo implementar carga, almacenamiento y descarga de archivos de forma segura, escalable y trazable.  
Su función es asegurar que los archivos se manejen con validación adecuada, almacenamiento persistente, thumbnails automáticos y políticas de lifecycle, sin comprometer seguridad ni performance.

Esta skill complementa `backend-api` (endpoints) y `security` (validación). Mientras esos definen la API y la seguridad general, esta skill define el flujo específico de archivos binarios.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué patrón de upload usar (multipart, chunked, streaming, presigned URLs)?
2. ¿Qué proveedor de almacenamiento usar (S3, Azure Blob, GCS)?
3. ¿Cómo validar archivos (tipo MIME, tamaño, virus)?
4. ¿Cómo generar thumbnails y transformaciones?
5. ¿Cómo gestionar el lifecycle de archivos (retención, archival, eliminación)?

## Relación con otras skills

- `backend-api` define los endpoints que esta skill implementa para upload/download.
- `security` define las validaciones de seguridad (CORS, inyección, CSRF).
- `authentication` proporciona la identidad del usuario que sube el archivo.
- `authorization` define quién puede subir/descargar/borrar archivos.
- `database-sp` puede almacenar metadata de archivos en la BD.

## Qué debe hacer el agente cuando esta skill está activa

1. Seleccionar el patrón de upload según tamaño y tipo de archivo.
2. Configurar el proveedor de almacenamiento (S3/Azure Blob/GCS).
3. Implementar validación de archivos (tipo MIME, tamaño, extensión).
4. Configurar virus scanning si el contexto lo requiere.
5. Definir la estructura de carpetas/blobs en el almacenamiento.
6. Implementar generación de thumbnails para imágenes.
7. Configurar CDN para archivos públicos.
8. Definir políticas de lifecycle (retención, archival, eliminación).
9. Implementar endpoints de upload, download y delete.
10. Definir el esquema de metadata de archivos en la BD.

## Entradas esperadas

Esta skill asume que ya existe:
- estructura de endpoints (`backend-api`);
- validaciones de seguridad (`security`);
- autenticación y autorización (`authentication`, `authorization`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- patrones de upload (multipart, chunked, streaming, presigned URLs);
- configuración de blob storage;
- validación de archivos (MIME, tamaño, extensión);
- virus scanning;
- generación de thumbnails;
- CDN integration;
- políticas de lifecycle;
- endpoints de upload, download y delete;
- metadata de archivos en la BD.

La fase no incluye todavía:
- edición de archivos en el navegador (crop, rotate);
- OCR o procesamiento de documentos;
- streaming de video/audio;
- sistema de DAM (Digital Asset Management) completo.

## Principios que siempre debe respetar

- Los archivos NUNCA deben almacenarse en el filesystem del servidor de aplicación.
- La validación de tipo MIME DEBE usar magic bytes, no solo la extensión.
- El tamaño máximo de archivo DEBE estar limitado por configuración, no hardcodeado.
- Los nombres de archivo almacenados DEBEN ser generados (UUID), no el nombre original.
- Los archivos DEBEN tener metadata en la BD (nombre original, tipo, tamaño, fecha, usuario).
- Las URLs de descarga DEBEN ser temporales (presigned URLs) para archivos privados.
- Los archivos eliminados DEBEN marcar la BD como soft-delete, no borrar el blob inmediatamente.
- Los uploads DEBEN ser asíncronos cuando el archivo supere un tamaño umbral.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- el patrón de upload según el caso;
- el proveedor y configuración de almacenamiento;
- la estructura de carpetas/blobs;
- la validación de archivos;
- las políticas de lifecycle;

Esta skill delega:
- la estructura general de endpoints a `backend-api`;
- la validación de seguridad general a `security`;
- la autenticación del usuario a `authentication`;
- el almacenamiento de metadata en BD a `database-sp`.

## Qué debe definir el diseño

### 1. Patrones de upload

| Patrón | Tamaño máximo | Pros | Contras | Uso |
|--------|---------------|------|---------|-----|
| **Multipart form-data** | 5-10 MB | Simple, estándar | Todo por el servidor | Avatares, documentos pequeños |
| **Chunked upload** | 100 MB - 1 GB | Resume, progress | Complejo | Videos, archivos grandes |
| **Presigned URL** | Sin límite | Directo a S3, sin servidor | Requiere cliente S3 | Cualquier tamaño, batches |
| **Streaming** | Variable | Eficiencia de memoria | Complejo, no resume | Descarga, streaming |

**Decisión por defecto**:
- archivos < 10 MB → multipart form-data;
- archivos 10-500 MB → presigned URL;
- archivos > 500 MB → chunked upload.

### 2. Estructura de almacenamiento

```
{bucket}/{tenant}/{entity}/{guid}/{filename}
                                          
Ejemplo:
/uploads/tenant-123/orders/550e8400-e29b-41d4-a716-446655440000/invoice.pdf
/uploads/tenant-123/users/550e8400-e29b-41d4-a716-446655440001/avatar.jpg
/uploads/tenant-123/products/550e8400-e29b-41d4-a716-446655440002/photo.png
```

Reglas:
- El nombre del archivo en storage es un UUID, nunca el nombre original.
- La carpeta incluye tenant para aislamiento multi-tenant.
- La carpeta incluye entidad (orders, users, products) para organización.
- Los thumbnails se almacenan en `{bucket}/{tenant}/{entity}/{guid}/thumb_{size}`.

### 3. Validación de archivos

```typescript
// src/core/upload/validation.ts

const ALLOWED_MIME_TYPES = {
  image: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  document: ['application/pdf', 'application/msword',
             'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  spreadsheet: ['application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
};

const MAX_FILE_SIZE = {
  image: 5 * 1024 * 1024,      // 5 MB
  document: 25 * 1024 * 1024,   // 25 MB
  spreadsheet: 10 * 1024 * 1024, // 10 MB
};

export function validateFile(
  file: { mimetype: string; size: number; originalname: string },
  category: keyof typeof ALLOWED_MIME_TYPES
): { valid: boolean; error?: string } {
  const allowedMimes = ALLOWED_MIME_TYPES[category];
  const maxSize = MAX_FILE_SIZE[category];

  if (!allowedMimes.includes(file.mimetype)) {
    return { valid: false, error: `File type ${file.mimetype} not allowed for ${category}` };
  }

  if (file.size > maxSize) {
    return { valid: false, error: `File size ${file.size} exceeds limit ${maxSize}` };
  }

  // Validate extension matches MIME type
  const ext = file.originalname.split('.').pop()?.toLowerCase();
  const mimeToExt: Record<string, string[]> = {
    'image/jpeg': ['jpg', 'jpeg'],
    'image/png': ['png'],
    'application/pdf': ['pdf'],
  };

  const expectedExts = mimeToExt[file.mimetype];
  if (expectedExts && ext && !expectedExts.includes(ext)) {
    return { valid: false, error: `Extension .${ext} doesn't match MIME type ${file.mimetype}` };
  }

  return { valid: true };
}
```

### 4. Magic bytes validation (server-side)

```python
# src/uploads/validators.py

MAGIC_BYTES: dict[str, bytes] = {
    "image/jpeg": bytes([0xFF, 0xD8, 0xFF]),
    "image/png": bytes([0x89, 0x50, 0x4E, 0x47]),
    "image/gif": bytes([0x47, 0x49, 0x46]),
    "application/pdf": bytes([0x25, 0x50, 0x44, 0x46]),
}


def validate_magic_bytes(file_content: bytes, expected_mime_type: str) -> bool:
    """Validate file content matches expected MIME type via magic bytes."""
    expected_bytes = MAGIC_BYTES.get(expected_mime_type)
    if expected_bytes is None:
        return True  # No magic bytes defined, allow

    return file_content[:len(expected_bytes)] == expected_bytes
```

### 5. Endpoint de upload (multipart)

```python
# src/api/upload/routes.py

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from pathlib import Path

router = APIRouter(prefix="/api/v1/files", tags=["Files"])


@router.post("/upload", summary="Upload a file")
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form(...),
    storage: IFileStorageService = Depends(),
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    validation = validate_file(
        {"mimetype": file.content_type, "size": file.size, "originalname": file.filename},
        category,
    )
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation.get("error"),
        )

    file_id = uuid4()
    stored_name = f"{file_id.hex}{Path(file.filename).suffix}"
    content = await file.read()

    await storage.upload(
        container=category,
        path=f"{tenant_id}/{category}/{file_id}",
        file_name=stored_name,
        content=content,
        content_type=file.content_type,
    )

    metadata = FileMetadata(
        id=file_id,
        original_name=file.filename,
        stored_name=stored_name,
        content_type=file.content_type,
        size=file.size,
        category=category,
        uploaded_by=user_id,
        uploaded_at=datetime.now(timezone.utc),
        record_status="A",
        record_creation_user=user_id,
        record_creation_date=datetime.now(timezone.utc),
    )

    await mediator.send(CreateFileMetadataCommand(metadata))

    return {
        "success": True,
        "data": {
            "id": str(file_id),
            "url": storage.get_presigned_url(stored_name, category),
        },
    }
```

### 6. Presigned URL para descarga

```python
@router.get("/{file_id}/download", summary="Download a file")
async def download_file(
    file_id: UUID,
    storage: IFileStorageService = Depends(),
):
    metadata = await storage.get_metadata(file_id)
    if metadata is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    presigned_url = storage.get_presigned_url(
        metadata.stored_name,
        metadata.category,
        expiration=timedelta(minutes=15),
    )

    return {
        "success": True,
        "data": {
            "url": presigned_url,
            "original_name": metadata.original_name,
            "content_type": metadata.content_type,
            "size": metadata.size,
        },
    }
```

### 7. Metadata de archivo en la BD

```sql
CREATE TABLE {schema}.file_metadata (
    file_metadata_id UUID NOT NULL DEFAULT gen_random_uuid(),
    stored_name VARCHAR(500) NOT NULL,
    original_name VARCHAR(500) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    size_bytes BIGINT NOT NULL,
    category VARCHAR(50) NOT NULL,
    entity_id UUID NULL,
    tenant_id UUID NOT NULL,
    thumbnail_generated BOOLEAN NOT NULL DEFAULT FALSE,
    virus_scan_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    record_creation_user VARCHAR(50) NOT NULL,
    record_creation_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    record_edit_user VARCHAR(50) NULL,
    record_edit_date TIMESTAMPTZ NULL,
    record_status CHAR(1) NOT NULL DEFAULT 'A',
    CONSTRAINT pk_{schema}_file_metadata PRIMARY KEY (file_metadata_id)
);
```

### 8. Políticas de lifecycle

| Tipo de archivo | Retención | Archival | Eliminación |
|----------------|-----------|----------|-------------|
| Documentos | 7 años | Mover a cold storage a los 2 años | Eliminar a los 7 años |
| Imágenes de perfil | Indefinido | N/A | Soft-delete al eliminar cuenta |
| Thumbnails | Igual que original | N/A | Eliminar con el original |
| Temporales (chunked upload) | 24 horas | N/A | Eliminar automáticamente |

## Preguntas guía

### 1. Sobre almacenamiento
- ¿Se usa S3, Azure Blob o GCS?
- ¿Se necesita CDN para archivos públicos?
- ¿El almacenamiento es por tenant o compartido?

### 2. Sobre upload
- ¿Cuál es el tamaño máximo de archivo esperado?
- ¿Se necesita chunked upload o presigned URLs?
- ¿Se necesita progress bar en el frontend?

### 3. Sobre seguridad
- ¿Se requiere virus scanning?
- ¿Los archivos son privados o públicos?
- ¿Se necesita encriptación en reposo?

### 4. Sobre thumbnails
- ¿Qué tamaños de thumbnail se necesitan?
- ¿Se generan automáticamente al subir?
- ¿Se usa CDN para entregar thumbnails?

### 5. Sobre lifecycle
- ¿Cuánto tiempo se retienen los archivos?
- ¿Hay requisitos regulatorios de retención?
- ¿Cómo se limpian los archivos temporales?

## Salidas esperadas de esta skill

### A. Servicio de almacenamiento
- Interfaz `IFileStorageService` con métodos upload, download, delete, getPresignedUrl.
- Implementación para S3/Azure Blob/GCS.

### B. Validación de archivos
- Validación de tipo MIME con magic bytes.
- Validación de tamaño por categoría.
- Validación de extensión vs MIME type.

### C. Endpoints de upload/download/delete
- `POST /api/v1/files/upload` — multipart upload.
- `GET /api/v1/files/{id}/download` — presigned URL.
- `DELETE /api/v1/files/{id}` — soft-delete.

### D. Tabla de metadata en BD
- `FileMetadata` con nombre original, stored name, tipo, tamaño, categoría, usuario, fecha.

### E. Generación de thumbnails
- Servicio `IThumbnailService` con generación automática al subir imágenes.

### F. Consumidores de esta skill
- `angular` consume los endpoints con un componente `<app-file-upload>`;
- `security` valida que los archivos cumplen las reglas de seguridad;
- `database-sp` almacena la metadata de archivos;
- `playwright` testea el flujo completo de upload/download.

## Criterios de calidad

- Los archivos se almacenan en blob storage, nunca en filesystem del servidor.
- Los nombres almacenados son UUID, no los originales.
- La validación usa magic bytes, no solo extensión.
- Los tamaños máximos están en configuración, no hardcodeados.
- Las URLs de descarga son temporales (presigned).
- Los archivos eliminados se marcan como soft-delete.
- Los uploads grandes usan presigned URLs o chunked upload.
- La metadata se almacen en la BD con columnas de auditoría.

## Comportamiento esperado del agente

Cuando el usuario pida guardar archivos en el filesystem del servidor, el agente debe rechazar y proponer blob storage.  
Cuando el usuario no valide el tipo de archivo, el agente debe advertir sobre MIME spoofing y proponer validación con magic bytes.  
Cuando el usuario necesite archivos de más de 10 MB, el agente debe proponer presigned URLs.  
Cuando el usuario elimine un archivo sin soft-delete, el agente debe proponer marcar la BD como inactiva antes de eliminar el blob.

## Checklist final de la skill

- ¿Se seleccionó el proveedor de almacenamiento (S3/Azure Blob/GCS)?
- ¿Se definió el patrón de upload según tamaño?
- ¿La validación usa magic bytes?
- ¿Los nombres almacenados son UUID?
- ¿Las URLs de descarga son temporales?
- ¿Se creó la tabla de metadata en la BD?
- ¿Se implementó soft-delete?
- ¿Se configuraron políticas de lifecycle?
- ¿Se generó thumbnail para imágenes?
- ¿Se configuró CDN si se requiere?
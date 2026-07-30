---
name: export-excel
description: 'Full Excel export pattern: database query, backend handler, endpoint,
  and frontend download hook. Trigger: When implementing Excel export, data download,
  or export button.'
version: 1.1
metadata:
  phase:
  - construction
  layer:
  - database
  - backend
  - frontend
  enforcement: recommended
  depends_on:
  - database-sp
  - data-access
  - react-services
  - angular-services
  consumed_by:
  - agent-fullstack
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: skill-contract
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Reuse existing list SP/query with `IsExport` flag | ALWAYS | No separate export SP |
| Export block BEFORE pagination block | ALWAYS | Avoid OFFSET/FETCH on export |
| Pass page=1, pageSize=1 from handler when IsExport=true | ALWAYS | DB parameters still required |
| Use string type for dates in backend request | RECOMMENDED | date handling |
| Verify error in first result row before generating file | ALWAYS | SP/query may return error |

## Pattern Overview
```
SP/Query (add IsExport flag) → Backend Handler (openpyxl (Python) or equiv) →
Export Endpoint → Frontend (service + component download trigger → button)
```

## Database Layer (PostgreSQL Function)
```sql
-- Add @ParamIIsExport BIT = 0 to existing list SP
-- Export block goes BEFORE pagination:
---------------------------------------------------------------
-- STEP: EXPORT (before pagination)
---------------------------------------------------------------
IF @ParamIIsExport = 1
BEGIN
    SELECT
        e.EntityId,
        e.Name,
        e.Amount,
        e.RecordCreationDate
        FROM {schema}.{entity} e
    WHERE e.RecordStatus = 'A'
    -- apply same filters as list
    ORDER BY e.RecordCreationDate DESC;
    RETURN;
END
-- Then the normal paginated block follows
```

## Backend Handler (Python + openpyxl)
```python
import io
import base64
from datetime import datetime, timezone
from openpyxl import Workbook

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


async def handle_export(request: ExportRequest, db: AsyncSession) -> ExportResponse:
    """Genera archivo Excel desde los datos obtenidos de la base de datos."""
    params = {
        "entity": request.entity,
        "is_export": True,
        "page": 1,
        "page_size": 1,
        **request.filters,
    }
    result = await db.execute(
        text(f"SELECT * FROM {request.schema}.list_{request.entity}"),
        params,
    )
    records = result.fetchall()

    if not records:
        raise HTTPException(status_code=404, detail="No hay datos para exportar")

    # Verificar errores en primera fila (si el SP/query devuelve errores)
    first_row = records[0]
    if hasattr(first_row, "error_code") and first_row.error_code:
        raise HTTPException(
            status_code=400,
            detail=first_row.error_message or "Error en la consulta",
        )

    # Generar Excel con openpyxl
    workbook: Workbook = Workbook()
    sheet = workbook.active
    sheet.title = "{Entity}"

    # Headers con estilo
    sheet.cell(row=1, column=1, value="ID")
    sheet.cell(row=1, column=2, value="Name")

    # Data rows
    row: int = 2
    for item in records:
        sheet.cell(row=row, column=1, value=getattr(item, "EntityId", ""))
        sheet.cell(row=row, column=2, value=getattr(item, "Name", "") or "")
        row += 1

    # Guardar a BytesIO y convertir a base64
    stream: io.BytesIO = io.BytesIO()
    workbook.save(stream)
    file_base64: str = base64.b64encode(stream.getvalue()).decode("utf-8")

    return ExportResponse(
        file_base64=file_base64,
        file_name=f"{{Entity}}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
```

## Python Alternative (openpyxl)
```python
async def export_entities(params: ExportParams, db: AsyncSession):
    rows = await db.execute(text("EXEC Schema.ListEntity @IsExport = 1 ..."))
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ID", "Name", "Amount"])
    for row in rows:
        ws.append([row.entity_id, row.name, row.amount])
    # Return as base64 or stream
```

## Frontend Hooks (React + @tanstack/react-query)
```typescript
// export.api.ts
async function exportEntities(params: ExportParams): Promise<Blob> {
  const res = await fetch(`/api/v1/entities/export?${toQueryString(params)}`);
  if (!res.ok) throw new Error('Export failed');
  return res.blob();
}

async function getExportEstimate(params: ExportParams): Promise<ExportEstimate> {
  const res = await fetch(`/api/v1/entities/export/estimate?${toQueryString(params)}`);
  if (!res.ok) throw new Error('Estimate failed');
  return res.json();
}

// use-export-entities.query.ts
import { useQuery } from '@tanstack/react-query';

export function useExportEntities(params: ExportParams, enabled: boolean) {
  return useQuery({
    queryKey: ['export', 'entities', params],
    queryFn: () => exportEntities(params),
    enabled,
    staleTime: Infinity,
    retry: false,
  });
}
```

## Frontend Component (React + Ant Design)
```tsx
import { useEffect, useState } from 'react';
import { Button, Progress, message } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { useExportEntities } from './use-export-entities.query';
import { getExportEstimate } from './export.api';

interface ExportButtonProps {
  params: ExportParams;
  disabled?: boolean;
  label?: string;
}

export function ExportButton({ params, disabled = false, label = 'Exportar Excel' }: ExportButtonProps) {
  const [enabled, setEnabled] = useState(false);
  const [progress, setProgress] = useState(0);
  const [estimatedSize, setEstimatedSize] = useState('');

  const exportResult = useExportEntities(params, enabled);

  useEffect(() => {
    if (exportResult.data) {
      downloadBlob(exportResult.data);
      setEnabled(false);
      setProgress(100);
      message.success('Exportación completada');
      const timeout = setTimeout(() => setProgress(0), 3000);
      return () => clearTimeout(timeout);
    }
  }, [exportResult.data]);

  useEffect(() => {
    if (exportResult.error) {
      setEnabled(false);
      setProgress(0);
      message.error(exportResult.error.message || 'Error al exportar');
    }
  }, [exportResult.error]);

  const handleExport = async () => {
    try {
      const estimate = await getExportEstimate(params);
      const sizeMb = (estimate.estimatedBytes / 1024 / 1024).toFixed(1);
      setEstimatedSize(`(~${sizeMb} MB)`);
    } catch {
      // Ignorar si no hay estimación
    }

    setProgress(50);
    setEnabled(true);
  };

  const downloadBlob = (data: Blob): void => {
    const url = window.URL.createObjectURL(data);
    const link = document.createElement('a');
    link.href = url;
    link.download = `export_${Date.now()}.xlsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  return (
    <>
      <Button
        icon={<DownloadOutlined />}
        loading={exportResult.isLoading}
        disabled={disabled || exportResult.isLoading}
        onClick={handleExport}
      >
        {label} {estimatedSize && !exportResult.isLoading ? estimatedSize : ''}
      </Button>

      {progress > 0 && progress < 100 && (
        <Progress percent={progress} showInfo={false} style={{ width: 100 }} />
      )}

      {progress === 100 && <Progress percent={100} type="circle" size={24} status="success" />}
    </>
  );
}
```

## Frontend Service (Angular + @ngneat/query)
```typescript
@Injectable({ providedIn: 'root' })
export class ExportService {
  private readonly http = inject(HttpClient);

  exportEntities(params: ExportParams): Observable<Blob> {
    return this.http.get('/api/v1/entities/export', {
      params: toHttpParams(params),
      responseType: 'blob',
    });
  }

  getExportEstimate(params: ExportParams): Observable<ExportEstimate> {
    return this.http.get<ExportEstimate>('/api/v1/entities/export/estimate', {
      params: toHttpParams(params),
    });
  }
}

// Hook wrapper con @ngneat/query
@Injectable({ providedIn: 'root' })
export class ExportQuery {
  private readonly queryClient = inject(QueryClient);
  private readonly exportService = inject(ExportService);

  useExportEntities(params: Signal<ExportParams>, enabled: Signal<boolean>) {
    return injectQuery(() => ({
      queryKey: computed(() => ['export', 'entities', params()]),
      queryFn: () => firstValueFrom(this.exportService.exportEntities(params())),
      enabled,
      staleTime: Infinity,
      retry: false,
    }));
  }
}
```

## Frontend Component (Angular + Ant Design)
```typescript
@Component({
  selector: 'app-export-button',
  template: `
    <button
      nz-button
      [nzLoading]="isLoading()"
      [disabled]="disabled() || isLoading()"
      (click)="handleExport()"
    >
      <span nz-icon nzType="download"></span>
      {{ label() }} {{ estimatedSize() && !isLoading() ? estimatedSize() : '' }}
    </button>

    @if (progress() > 0 && progress() < 100) {
      <nz-progress
        [nzPercent]="progress()"
        [nzShowInfo]="false"
        [nzStyle]="{ width: '100px' }"
      ></nz-progress>
    }

    @if (progress() === 100) {
      <nz-progress
        [nzPercent]="100"
        nzType="circle"
        [nzWidth]="24"
        nzStatus="success"
      ></nz-progress>
    }
  `,
})
export class ExportButtonComponent {
  params = input.required<ExportParams>();
  disabled = input(false);
  label = input('Exportar Excel');

  private readonly exportQuery = inject(ExportQuery);
  private readonly message = inject(NzMessageService);

  protected readonly enabled = signal(false);
  protected readonly progress = signal(0);
  protected readonly estimatedSize = signal<string>('');

  protected readonly exportResult = this.exportQuery.useExportEntities(
    this.params,
    this.enabled
  );

  protected readonly isLoading = computed(() => this.exportResult.isLoading());

  constructor() {
    effect(() => {
      const data = this.exportResult.data();
      if (data) {
        this.downloadBlob(data);
        this.enabled.set(false);
        this.progress.set(100);
        this.message.success('Exportación completada');
        setTimeout(() => this.progress.set(0), 3000);
      }
    });

    effect(() => {
      const error = this.exportResult.error();
      if (error) {
        this.enabled.set(false);
        this.progress.set(0);
        this.message.error(error.message || 'Error al exportar');
      }
    });
  }

  protected async handleExport(): Promise<void> {
    try {
      const estimate = await firstValueFrom(
        this.exportService.getExportEstimate(toSignalValue(this.params))
      );
      const sizeMb = (estimate.estimatedBytes / 1024 / 1024).toFixed(1);
      this.estimatedSize.set(`(~${sizeMb} MB)`);
    } catch {
      // Ignorar si no hay estimación
    }

    this.progress.set(50);
    this.enabled.set(true);
  }

  private downloadBlob(data: Blob): void {
    const url = window.URL.createObjectURL(data);
    const link = document.createElement('a');
    link.href = url;
    link.download = `export_${Date.now()}.xlsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}
```

## Patrón completo export-excel multi-stack

### Base de datos

El flag `IsExport` se añade al SP/query de listado existente. El bloque de exportación debe colocarse SIEMPRE antes del bloque de paginación para evitar que `OFFSET/FETCH` limite los resultados.

#### PostgreSQL — Function con columnas dinámicas

```sql
-- Schema.sp_{Entity}_List
-- @ParamIIsExport BIT = 0
-- @ParamIDynamicColumns TEXT = NULL  -- columnas separadas por coma
CREATE PROCEDURE [{Schema}].[sp_{Entity}_List]
    @ParamIUserId          INT,
    @ParamISearchTerm      VARCHAR(100) = NULL,
    @ParamIFilterStatus    VARCHAR(20)  = NULL,
    @ParamIPage            INT           = 1,
    @ParamIPageSize        INT           = 10,
    @ParamISortColumn      VARCHAR(50)   = 'RecordCreationDate',
    @ParamISortDirection   VARCHAR(4)    = 'DESC',
    @ParamIIsExport        BIT           = 0,
    @ParamIDynamicColumns  TEXT = NULL
AS
BEGIN
    -- PostgreSQL: no SET NOCOUNT needed

    DECLARE @Sql   TEXT;
    DECLARE @Where TEXT = 'WHERE e.RecordStatus = ''A''';
    DECLARE @Params TEXT = N'
        @UserId INT,
        @SearchTerm VARCHAR(100),
        @FilterStatus VARCHAR(20)
    ';

    -- Filtros dinámicos
    IF @ParamISearchTerm IS NOT NULL
        SET @Where = @Where + ' AND (e.Name LIKE ''%'' + @SearchTerm + ''%'' OR e.Code LIKE ''%'' + @SearchTerm + ''%'')';
    IF @ParamIFilterStatus IS NOT NULL
        SET @Where = @Where + ' AND e.Status = @FilterStatus';

    -- Columnas por defecto o dinámicas
    DECLARE @Columns TEXT = '
        e.{Entity}Id   AS Id,
        e.Name         AS Nombre,
        e.Code         AS Codigo,
        e.Status       AS Estado,
        e.RecordCreationDate AS FechaCreacion
    ';
    IF @ParamIDynamicColumns IS NOT NULL
        SET @Columns = @ParamIDynamicColumns;

    ---------------------------------------------------------------
    -- STEP: EXPORT (before pagination)
    ---------------------------------------------------------------
    IF @ParamIIsExport = 1
    BEGIN
        SET @Sql = N'
            SELECT ' + @Columns + N'
            FROM {schema}.{entity} e
            ' + @Where + N'
            ORDER BY e.' + @ParamISortColumn + ' ' + @ParamISortDirection + N';
        ';
        EXEC sp_executesql @Sql, @Params,
            @UserId = @ParamIUserId,
            @SearchTerm = @ParamISearchTerm,
            @FilterStatus = @ParamIFilterStatus;
        RETURN;
    END

    ---------------------------------------------------------------
    -- STEP: PAGINATED LIST
    ---------------------------------------------------------------
    SET @Sql = N'
        SELECT
            ' + @Columns + N',
            COUNT(*) OVER() AS TotalCount
            FROM {schema}.{entity} e
        ' + @Where + N'
        ORDER BY e.' + @ParamISortColumn + ' ' + @ParamISortDirection + N'
        OFFSET (@Page - 1) * @PageSize ROWS
        FETCH NEXT @PageSize ROWS ONLY;
    ';
    EXEC sp_executesql @Sql,
        N'@Page INT, @PageSize INT, @UserId INT, @SearchTerm VARCHAR(100), @FilterStatus VARCHAR(20)',
        @Page = @ParamIPage,
        @PageSize = @ParamIPageSize,
        @UserId = @ParamIUserId,
        @SearchTerm = @ParamISearchTerm,
        @FilterStatus = @ParamIFilterStatus;
END
```

#### PostgreSQL — Función con refcursor

```sql
CREATE OR REPLACE FUNCTION {schema}.fn_{entity}_list(
    p_user_id          INT,
    p_search_term      VARCHAR(100) DEFAULT NULL,
    p_filter_status    VARCHAR(20)  DEFAULT NULL,
    p_page             INT          DEFAULT 1,
    p_page_size        INT          DEFAULT 10,
    p_sort_column      VARCHAR(50)  DEFAULT 'record_creation_date',
    p_sort_direction   VARCHAR(4)   DEFAULT 'DESC',
    p_is_export        BOOLEAN      DEFAULT FALSE,
    p_dynamic_columns  TEXT         DEFAULT NULL
)
RETURNS REFCURSOR
LANGUAGE plpgsql
AS $$
DECLARE
    v_columns TEXT;
    v_where   TEXT := 'WHERE e.record_status = ''A''';
    v_sql     TEXT;
    v_ref     REFCURSOR := 'export_cursor';
BEGIN
    IF p_search_term IS NOT NULL THEN
        v_where := v_where || ' AND (e.name ILIKE ''%'' || p_search_term || ''%'' OR e.code ILIKE ''%'' || p_search_term || ''%'')';
    END IF;
    IF p_filter_status IS NOT NULL THEN
        v_where := v_where || ' AND e.status = p_filter_status';
    END IF;

    v_columns := COALESCE(p_dynamic_columns, '
        e.{entity}_id     AS id,
        e.name            AS nombre,
        e.code            AS codigo,
        e.status          AS estado,
        e.record_creation_date AS fecha_creacion
    ');

    IF p_is_export THEN
        v_sql := format('SELECT %s FROM {schema}.{entity} e %s ORDER BY e.%I %s',
            v_columns, v_where, p_sort_column, p_sort_direction);
        OPEN v_ref FOR EXECUTE v_sql
            USING p_user_id, p_search_term, p_filter_status;
        RETURN v_ref;
    ELSE
        v_sql := format('SELECT %s, COUNT(*) OVER() AS total_count FROM {schema}.{entity} e %s ORDER BY e.%I %s OFFSET ($1 - 1) * $2 LIMIT $2',
            v_columns, v_where, p_sort_column, p_sort_direction);
        OPEN v_ref FOR EXECUTE v_sql
            USING p_page, p_page_size, p_user_id, p_search_term, p_filter_status;
        RETURN v_ref;
    END IF;
END;
$$;
```

### Backend handler

Cada stack implementa el mismo patrón: recibir parámetros de filtro, llamar al SP/query con `IsExport=true`, mapear resultados y generar el archivo Excel.

#### Python — openpyxl + SQLAlchemy

```python
import io
from datetime import datetime, timezone

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse


async def export_async(request: ExportRequest, db: AsyncSession) -> StreamingResponse:
    """Genera y retorna un archivo Excel con los datos filtrados."""

    # 1. Obtener datos con SQLAlchemy (SP/query con IsExport=True)
    result = await db.execute(
        text("SELECT * FROM {Schema}.sp_{Entity}_List(:user_id, :search_term, "
             ":filter_status, :page, :page_size, :sort_column, :sort_direction, "
             ":is_export, :dynamic_columns)"),
        {
            "user_id": request.user_id,
            "search_term": request.search_term,
            "filter_status": request.filter_status,
            "page": 1,
            "page_size": 1,
            "sort_column": request.sort_column,
            "sort_direction": request.sort_direction,
            "is_export": True,
            "dynamic_columns": request.dynamic_columns,
        },
    )
    rows = result.fetchall()

    # 2. Validar error en primera fila
    if not rows:
        raise HTTPException(status_code=404, detail="No hay datos para exportar")
    first_row = rows[0]
    if hasattr(first_row, "error_code") and first_row.error_code:
        raise HTTPException(
            status_code=400,
            detail=getattr(first_row, "error_message", "Error en la consulta"),
        )

    # 3. Generar Excel con openpyxl
    workbook: Workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Exportacion"

    # 3a. Escribir headers desde el diccionario de columnas
    column_map: dict[str, str] = get_column_mapping(request.language)
    col_index: int = 1
    header_fill: PatternFill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
    header_font: Font = Font(bold=True)

    for col in request.selected_columns:
        cell = sheet.cell(row=1, column=col_index, value=column_map.get(col, col))
        cell.font = header_font
        cell.fill = header_fill
        col_index += 1

    # 3b. Escribir datos
    row_num: int = 2
    for item in rows:
        col_index = 1
        for col in request.selected_columns:
            value = getattr(item, col, None)
            sheet.cell(row=row_num, column=col_index, value=str(value) if value else "")
            col_index += 1
        row_num += 1

    # 3c. Autoajuste de columnas
    for idx, _col_name in enumerate(request.selected_columns, 1):
        sheet.column_dimensions[get_column_letter(idx)].auto_size = True

    # 4. Escribir a stream y retornar
    stream: io.BytesIO = io.BytesIO()
    workbook.save(stream)
    stream.seek(0)

    file_name: str = (
        f"Exportacion_{request.entity_name}_"
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H%M%S')}.xlsx"
    )

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )
```

#### Java — Apache POI + Spring Data JPA

```java
public ResponseEntity<Resource> export(ExportRequest request) {
    // 1. Obtener datos vía JPA o native query
    List<Object[]> rows = entityManager.createNativeQuery(
        "SELECT e.id, e.name, e.code, e.status, e.created_at " +
        "FROM entities e WHERE e.record_status = 'A' " +
        "AND (:searchTerm IS NULL OR e.name LIKE :searchTerm) " +
        "ORDER BY e.created_at DESC"
    )
    .setParameter("searchTerm", request.getSearchTerm())
    .getResultList();

    // 2. Generar Excel con Apache POI
    Workbook workbook = new XSSFWorkbook();
    Sheet sheet = workbook.createSheet("Exportacion");

    // Header style
    CellStyle headerStyle = workbook.createCellStyle();
    headerStyle.setFillForegroundColor(IndexedColors.GREY_25_PERCENT.getIndex());
    headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
    XSSFFont headerFont = (XSSFFont) workbook.createFont();
    headerFont.setBold(true);
    headerStyle.setFont(headerFont);

    // Headers
    Row headerRow = sheet.createRow(0);
    String[] columns = {"ID", "Nombre", "Código", "Estado", "Fecha"};
    for (int i = 0; i < columns.length; i++) {
        Cell cell = headerRow.createCell(i);
        cell.setCellValue(columns[i]);
        cell.setCellStyle(headerStyle);
    }

    // Data
    int rowNum = 1;
    for (Object[] rowData : rows) {
        Row row = sheet.createRow(rowNum++);
        for (int i = 0; i < rowData.length; i++) {
            row.createCell(i).setCellValue(
                rowData[i] != null ? rowData[i].toString() : ""
            );
        }
    }

    // Auto-size
    for (int i = 0; i < columns.length; i++) sheet.autoSizeColumn(i);

    // Response
    ByteArrayOutputStream out = new ByteArrayOutputStream();
    workbook.write(out);
    workbook.close();

    String filename = "Exportacion_" + LocalDate.now() + ".xlsx";

    return ResponseEntity.ok()
        .header(HttpHeaders.CONTENT_DISPOSITION,
            "attachment; filename=\"" + filename + "\"")
        .contentType(MediaType.parseMediaType(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
        .body(new ByteArrayResource(out.toByteArray()));
}
```

#### Python — openpyxl + SQLAlchemy

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from fastapi.responses import StreamingResponse
import io

async def export_entities(request: ExportRequest, db: AsyncSession):
    # 1. Query datos
    result = await db.execute(
        text("SELECT id, name, code, status, created_at FROM entities "
             "WHERE record_status = 'A' "
             "AND (:search IS NULL OR name ILIKE :search) "
             "ORDER BY created_at DESC"),
        {"search": f"%{request.search_term}%" if request.search_term else None}
    )
    rows = result.fetchall()

    # 2. Generar Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Exportacion"

    # Headers con estilo
    header_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
    header_font = Font(bold=True)

    columns = ["ID", "Nombre", "Código", "Estado", "Fecha"]
    for col, name in enumerate(columns, 1):
        cell = ws.cell(row=1, column=col, value=name)
        cell.fill = header_fill
        cell.font = header_font

    # Datos
    for row_idx, row in enumerate(rows, 2):
        for col_idx, value in enumerate(row, 1):
            ws.cell(row=row_idx, column=col_idx, value=str(value) if value else "")

    # Autoajuste
    for col in columns:
        ws.column_dimensions[get_column_letter(columns.index(col) + 1)].auto_size = True

    # 3. Streaming response
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"Exportacion_{datetime.utcnow().strftime('%Y-%m-%d')}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
```

#### Node.js — exceljs + pg

```typescript
import ExcelJS from 'exceljs';
import { Pool } from 'pg';

async function exportEntities(req: ExportRequest, res: Response) {
    const pool = new Pool();

    // 1. Query datos
    const result = await pool.query(
        `SELECT id, name, code, status, created_at
         FROM entities
         WHERE record_status = 'A'
         ${req.searchTerm ? "AND name ILIKE $1" : ""}
         ORDER BY created_at DESC`,
        req.searchTerm ? [`%${req.searchTerm}%`] : []
    );

    // 2. Generar Excel con exceljs
    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet('Exportacion');

    // Headers
    sheet.columns = [
        { header: 'ID', key: 'id', width: 10 },
        { header: 'Nombre', key: 'name', width: 30 },
        { header: 'Código', key: 'code', width: 15 },
        { header: 'Estado', key: 'status', width: 15 },
        { header: 'Fecha', key: 'created_at', width: 20 },
    ];

    // Header style
    const headerRow = sheet.getRow(1);
    headerRow.font = { bold: true };
    headerRow.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FFD9D9D9' }
    };

    // Data
    result.rows.forEach((row: any) => sheet.addRow(row));

    // 3. Streaming response
    const fileName = `Exportacion_${Date.now()}.xlsx`;

    res.setHeader(
        'Content-Type',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    );
    res.setHeader(
        'Content-Disposition',
        `attachment; filename="${fileName}"`
    );

    await workbook.xlsx.write(res);
    res.end();
}
```

### API endpoint

El endpoint de exportación debe configurarse como una ruta GET separada que devuelva el archivo binario directamente, no base64.

#### Contrato del endpoint

```
GET /api/v1/{entities}/export?searchTerm=&filterStatus=&sortColumn=&sortDirection=&language=es
Accept: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

#### Response exitoso

- **Status**: `200 OK`
- **Content-Type**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Content-Disposition**: `attachment; filename="Exportacion_Entities_2026-06-05_143022.xlsx"`
- **Body**: stream binario del archivo Excel

#### Response con error

- **Status**: `400 Bad Request` si los filtros son inválidos
- **Status**: `404 Not Found` si no hay datos
- **Status**: `500 Internal Server Error` si falla la generación
- **Body**: `{ "error": true, "message": "Descripción del error", "code": "EXPORT_ERROR" }`

#### Python FastAPI

```python
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

router: APIRouter = APIRouter(prefix="/api/v1", tags=["Export"])


@router.get(
    "/{entities}/export",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "Archivo Excel generado exitosamente",
            "content": {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}
            },
        },
        400: {"description": "Parámetros de filtro inválidos"},
        404: {"description": "No se encontraron datos para exportar"},
    },
)
async def export_entities(
    request: ExportRequest = Depends(),
    service: IExportService = Depends(get_export_service),
) -> StreamingResponse:
    """Exporta entidades a archivo Excel con los filtros especificados."""
    result = await service.export(request)
    return StreamingResponse(
        result.stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{result.file_name}"'
        },
    )
```

#### FastAPI

```python
@router.get("/api/v1/{entities}/export")
async def export_entities(
    request: ExportRequest = Depends(),
    service: IExportService = Depends(get_export_service)
):
    result = await service.export(request)

    return StreamingResponse(
        result.stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{result.filename}"'
        }
    )
```

#### Node Express

```typescript
router.get('/api/v1/:entities/export', async (req: Request, res: Response) => {
    try {
        const result = await exportService.export(req.query);

        res.setHeader(
            'Content-Type',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        );
        res.setHeader(
            'Content-Disposition',
            `attachment; filename="${result.fileName}"`
        );
        result.stream.pipe(res);
    } catch (error) {
        res.status(500).json({
            error: true,
            message: 'Error generating export',
            code: 'EXPORT_ERROR'
        });
    }
});
```

### Frontend service

El servicio de descarga debe usar `injectQuery` de @ngneat/query con configuración especial para blobs, y debe gestionar la descarga automática del archivo.

#### Service base con descarga blob

```typescript
@Injectable({ providedIn: 'root' })
export class ExportService {
  private readonly http = inject(HttpClient);

  exportEntities(params: ExportParams): Observable<{ blob: Blob; filename: string }> {
    return this.http.get('/api/v1/entities/export', {
      params: toHttpParams(params),
      responseType: 'blob',
      observe: 'response',
    }).pipe(
      map(response => {
        const disposition = response.headers.get('content-disposition');
        const filenameMatch = disposition?.match(/filename="?(.+?)"?$/);
        const filename = filenameMatch?.[1] || `export_${Date.now()}.xlsx`;
        return { blob: response.body!, filename };
      })
    );
  }

  getExportEstimate(params: ExportParams): Observable<ExportEstimate> {
    return this.http.get<ExportEstimate>('/api/v1/entities/export/estimate', {
      params: toHttpParams(params),
    });
  }
}
```

#### Componente botón con indicador de progreso

```typescript
@Component({
  selector: 'app-export-button',
  template: `
    <div class="export-button-container">
      <button
        nz-button
        [nzLoading]="isLoading()"
        [disabled]="disabled() || isLoading()"
        (click)="handleExport()"
      >
        <span nz-icon [nzType]="isLoading() ? 'loading' : 'download'"></span>
        {{ label() }} {{ estimatedSize() && !isLoading() ? estimatedSize() : '' }}
      </button>

      @if (progress() > 0 && progress() < 100) {
        <nz-progress
          [nzPercent]="progress()"
          [nzShowInfo]="false"
          [nzStyle]="{ width: '100px' }"
          nzStrokeColor="#1890ff"
        ></nz-progress>
      }

      @if (progress() === 100) {
        <nz-progress
          [nzPercent]="100"
          nzType="circle"
          [nzWidth]="24"
          nzStrokeColor="#52c41a"
        ></nz-progress>
      }
    </div>
  `,
  styles: [`
    .export-button-container {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  `],
})
export class ExportButtonComponent {
  params = input.required<ExportParams>();
  disabled = input(false);
  label = input('Exportar Excel');

  private readonly exportService = inject(ExportService);
  private readonly queryClient = inject(QueryClient);
  private readonly message = inject(NzMessageService);

  protected readonly enabled = signal(false);
  protected readonly progress = signal(0);
  protected readonly estimatedSize = signal<string>('');

  protected readonly exportQuery = injectQuery(() => ({
    queryKey: computed(() => ['export', 'entities', this.params()]),
    queryFn: () => firstValueFrom(this.exportService.exportEntities(this.params())),
    enabled: this.enabled,
    staleTime: Infinity,
    retry: false,
  }));

  protected readonly isLoading = computed(() => this.exportQuery.isLoading());

  constructor() {
    effect(() => {
      const data = this.exportQuery.data();
      if (data) {
        this.downloadBlob(data.blob, data.filename);
        this.enabled.set(false);
        this.progress.set(100);
        this.message.success('Exportación completada');
        setTimeout(() => this.progress.set(0), 3000);
      }
    });

    effect(() => {
      const error = this.exportQuery.error();
      if (error) {
        this.enabled.set(false);
        this.progress.set(0);
        this.message.error(error.message || 'Error al exportar');
      }
    });
  }

  protected async handleExport(): Promise<void> {
    // Estimar tamaño antes de exportar
    try {
      const estimate = await firstValueFrom(
        this.exportService.getExportEstimate(toSignalValue(this.params))
      );
      const sizeMb = (estimate.estimatedBytes / 1024 / 1024).toFixed(1);
      this.estimatedSize.set(`(~${sizeMb} MB)`);
    } catch {
      // Ignorar si no hay estimación
    }

    this.progress.set(50);
    this.enabled.set(true);
  }

  private downloadBlob(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}
```

#### Hook con estimación de tamaño

```typescript
@Injectable({ providedIn: 'root' })
export class ExportEstimateQuery {
  private readonly exportService = inject(ExportService);

  useExportEstimate(params: Signal<ExportParams>) {
    return injectQuery(() => ({
      queryKey: computed(() => ['export-estimate', params()]),
      queryFn: () => firstValueFrom(this.exportService.getExportEstimate(params())),
      staleTime: 30_000, // 30 segundos de caché
      enabled: false,     // Solo se ejecuta al llamar refetch()
    }));
  }
}
```

## Exportaciones grandes (streaming)

Para conjuntos de datos que exceden los 100,000 registros o 50 MB en memoria, el enfoque base64 en memoria no es viable. Se requiere streaming o procesamiento asíncrono.

### Cuándo usar streaming vs in-memory

| Factor | In-memory | Streaming |
|--------|-----------|-----------|
| Registros | < 100,000 | >= 100,000 |
| Tamaño estimado | < 50 MB | >= 50 MB |
| Tiempo de generación | < 5 segundos | >= 5 segundos |
| Usuarios concurrentes | < 50 | >= 50 |
| Timeout de request | Soportado | No aplica (respuesta progresiva) |
| Progreso visible | No necesario | Deseable |

### Patrón: escribir a temp file → stream response

En lugar de construir el Excel en memoria, se escribe a un archivo temporal y se va transmitiendo mientras se genera.

#### Python FastAPI con streaming a disco

```python
import io
import tempfile
import uuid
from datetime import datetime, timezone

from openpyxl import Workbook
from openpyxl.styles import Font
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse


async def export_large_async(request: ExportRequest, db: AsyncSession) -> FileResponse:
    """Exporta grandes volúmenes de datos usando archivo temporal y streaming."""
    temp_dir: str = tempfile.gettempdir()
    temp_file: str = f"{temp_dir}\\export_{uuid.uuid4()}.xlsx"

    try:
        workbook: Workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Exportacion"

        # Headers con estilo negrita
        bold_font: Font = Font(bold=True)
        cell_id = sheet.cell(row=1, column=1, value="ID")
        cell_id.font = bold_font
        cell_nombre = sheet.cell(row=1, column=2, value="Nombre")
        cell_nombre.font = bold_font

        # Leer datos en batches de 5000
        offset: int = 0
        batch_size: int = 5000
        row: int = 2
        has_more: bool = True

        while has_more:
            batch_result = await db.execute(
                text("SELECT * FROM {Schema}.sp_{Entity}_ExportBatch("
                     ":offset, :batch_size, :is_export)"),
                {
                    "offset": offset,
                    "batch_size": batch_size,
                    "is_export": True,
                },
            )
            batch_list = batch_result.fetchall()
            has_more = len(batch_list) == batch_size

            for item in batch_list:
                sheet.cell(row=row, column=1, value=getattr(item, "EntityId", ""))
                sheet.cell(row=row, column=2, value=getattr(item, "Name", "") or "")
                row += 1

            offset += batch_size

        # Guardar a archivo temporal
        workbook.save(temp_file)
        workbook.close()

        file_name: str = (
            f"Exportacion_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.xlsx"
        )

        return FileResponse(
            path=temp_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=file_name,
            background=None,  # No eliminar hasta que se complete la transmisión
        )
    except Exception:
        # Limpiar archivo temporal en caso de error
        if Path(temp_file).exists():
            Path(temp_file).unlink()
        raise
```

### Patrón background job (request → job → download URL)

Para exportaciones muy grandes (> 500,000 registros) que tardan minutos, se utiliza un job asíncrono.

#### Flujo

```
1. POST /api/v1/entities/export/job  →  { filters }
2. Response: { jobId: "guid", status: "processing" }
3. GET  /api/v1/entities/export/job/{jobId}/status  →  { status, progress, downloadUrl? }
4. GET  /downloads/{jobId}.xlsx  →  archivo listo
```

#### Endpoint para crear job

```python
import uuid

from fastapi import APIRouter, Depends, BackgroundTasks

router: APIRouter = APIRouter(prefix="/api/v1/entities/export", tags=["Export"])


@router.post("/job", status_code=202)
async def create_export_job(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    job_runner: IExportJobRunner = Depends(get_export_job_runner),
):
    """Crea un job asíncrono de exportación y retorna la URL de estado."""
    job_id: str = str(uuid.uuid4())

    # Encolar job en background (Celery / ARQ / BackgroundTasks)
    background_tasks.add_task(
        job_runner.run_export,
        job_id=job_id,
        request=request,
    )

    return {
        "job_id": job_id,
        "status": "processing",
        "status_url": f"/api/v1/entities/export/job/{job_id}/status",
    }
```

#### Endpoint de estado

```python
from fastapi import APIRouter, Depends, HTTPException

router: APIRouter = APIRouter(prefix="/api/v1/entities/export/job", tags=["Export"])


@router.get("/{job_id}/status")
async def get_export_job_status(
    job_id: str,
    tracker: IExportJobTracker = Depends(get_export_job_tracker),
):
    """Consulta el estado de un job de exportación."""
    status = await tracker.get_status(job_id)

    if status is None:
        raise HTTPException(
            status_code=404,
            detail={"error": True, "message": "Job not found"},
        )

    if status.is_completed:
        return {
            "job_id": job_id,
            "status": "completed",
            "progress": 100,
            "download_url": f"/downloads/{job_id}.xlsx",
            "file_name": status.file_name,
            "size_bytes": status.file_size,
        }

    if status.is_failed:
        return {
            "job_id": job_id,
            "status": "failed",
            "error": status.error_message,
        }

    return {
        "job_id": job_id,
        "status": "processing",
        "progress": status.progress,
        "estimated_seconds_remaining": status.estimated_seconds_remaining,
    }
```

### Progreso via WebSocket

Cuando el usuario está en la página esperando la exportación, se puede usar WebSocket para notificar el progreso en tiempo real.

#### WebSocket (FastAPI)

```python
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from openpyxl import Workbook


# Almacén de conexiones WebSocket agrupadas por job_id
class ConnectionManager:
    """Administra conexiones WebSocket agrupadas por job_id para notificar progreso."""

    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str) -> None:
        await websocket.accept()
        self._connections.setdefault(job_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, job_id: str) -> None:
        conns = self._connections.get(job_id, [])
        if websocket in conns:
            conns.remove(websocket)

    async def broadcast(self, job_id: str, message: dict[str, Any]) -> None:
        """Envía mensaje a todos los WebSockets suscritos al job_id."""
        for ws in self._connections.get(job_id, []):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(ws, job_id)


manager: ConnectionManager = ConnectionManager()
router_ws: APIRouter = APIRouter()


@router_ws.websocket("/ws/export/{job_id}")
async def websocket_export_progress(websocket: WebSocket, job_id: str) -> None:
    """WebSocket para recibir notificaciones de progreso de exportación."""
    await manager.connect(websocket, job_id)
    try:
        # Mantener conexión abierta; el job runner envía mensajes por broadcast
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)


# ── Desde el job runner ─────────────────────────────────────────────
async def run_export(job_id: str, request: ExportRequest) -> None:
    """Ejecuta exportación en background y notifica progreso vía WebSocket."""
    total: int = await db.scalar(text("SELECT COUNT(*) FROM ...")) or 0

    workbook: Workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Exportacion"
    processed: int = 0

    async for batch in get_batches(request):
        processed += len(batch)
        progress: int = int(processed / total * 100) if total > 0 else 0

        # Notificar progreso
        await manager.broadcast(
            job_id,
            {
                "type": "ExportProgress",
                "job_id": job_id,
                "progress": progress,
                "processed_rows": processed,
                "total_rows": total,
            },
        )

        # Escribir batch al sheet
        write_batch_to_sheet(sheet, batch, processed - len(batch) + 2)

    file_path: str = get_file_path(job_id)
    workbook.save(file_path)

    # Notificar completado
    await manager.broadcast(
        job_id,
        {
            "type": "ExportCompleted",
            "job_id": job_id,
            "download_url": f"/downloads/{job_id}.xlsx",
        },
    )
```

#### Frontend — suscripción WebSocket (React)

```typescript
// use-export-progress.ts
import { useCallback, useRef, useState } from 'react';
import { HubConnectionBuilder, LogLevel, type HubConnection } from '@microsoft/signalr';

export function useExportProgress() {
  const connectionRef = useRef<HubConnection | null>(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<'idle' | 'processing' | 'completed' | 'failed'>('idle');

  const subscribeToJob = useCallback((jobId: string) => {
    const connection = new HubConnectionBuilder()
      .withUrl('/hubs/export')
      .withAutomaticReconnect()
      .configureLogging(LogLevel.Warning)
      .build();

    connection.on('ExportProgress', (data: ExportProgress) => {
      setProgress(data.progress);
      setStatus('processing');
    });

    connection.on('ExportCompleted', (data: ExportComplete) => {
      setProgress(100);
      setStatus('completed');
      // Iniciar descarga automática
      const link = document.createElement('a');
      link.href = data.downloadUrl;
      link.click();
    });

    connection.on('ExportFailed', () => {
      setStatus('failed');
    });

    connection.start().then(() => {
      connection.invoke('SubscribeToJob', jobId);
    });

    connectionRef.current = connection;
  }, []);

  const unsubscribe = useCallback(() => {
    connectionRef.current?.stop();
    connectionRef.current = null;
    setProgress(0);
    setStatus('idle');
  }, []);

  return { progress, status, subscribeToJob, unsubscribe };
}
```

#### Frontend — suscripción WebSocket (Angular)

```typescript
@Injectable({ providedIn: 'root' })
export class ExportProgressService {
  private readonly hubConnection = signal<HubConnection | null>(null);

  readonly progress = signal(0);
  readonly status = signal<'idle' | 'processing' | 'completed' | 'failed'>('idle');

  subscribeToJob(jobId: string): void {
    const connection = new HubConnectionBuilder()
      .withUrl('/hubs/export')
      .withAutomaticReconnect()
      .configureLogging(LogLevel.Warning)
      .build();

    connection.on('ExportProgress', (data: ExportProgress) => {
      this.progress.set(data.progress);
      this.status.set('processing');
    });

    connection.on('ExportCompleted', (data: ExportComplete) => {
      this.progress.set(100);
      this.status.set('completed');
      // Iniciar descarga automática
      const link = document.createElement('a');
      link.href = data.downloadUrl;
      link.click();
    });

    connection.on('ExportFailed', () => {
      this.status.set('failed');
    });

    connection.start().then(() => {
      connection.invoke('SubscribeToJob', jobId);
    });

    this.hubConnection.set(connection);
  }

  unsubscribe(): void {
    this.hubConnection()?.stop();
    this.hubConnection.set(null);
    this.progress.set(0);
    this.status.set('idle');
  }
}
```

## Formato condicional

### Selección dinámica de columnas

Permitir al usuario elegir qué columnas incluir en la exportación antes de descargar.

#### Modal de selección de columnas (React)

```tsx
import { useEffect, useMemo, useState } from 'react';
import { Modal, Checkbox } from 'antd';

interface ExportColumnSelectorProps {
  columns: ColumnOption[];
  visible: boolean;
  onSubmit: (keys: string[]) => void;
  onCancel: () => void;
}

export function ExportColumnSelector({ columns, visible, onSubmit, onCancel }: ExportColumnSelectorProps) {
  const [selectedKeys, setSelectedKeys] = useState<string[]>([]);

  useEffect(() => {
    setSelectedKeys(columns.filter((c) => c.selected).map((c) => c.key));
  }, [columns]);

  const checkboxOptions = useMemo(
    () => columns.map((c) => ({ label: c.label, value: c.key })),
    [columns],
  );

  return (
    <Modal open={visible} title="Seleccionar columnas para exportar" onCancel={onCancel} onOk={() => onSubmit(selectedKeys)}>
      <Checkbox.Group
        value={selectedKeys}
        onChange={(values) => setSelectedKeys(values as string[])}
        options={checkboxOptions}
      />
    </Modal>
  );
}
```

#### Modal de selección de columnas (Angular)

```typescript
@Component({
  selector: 'app-export-column-selector',
  template: `
    <nz-modal
      [nzVisible]="visible()"
      nzTitle="Seleccionar columnas para exportar"
      (nzOnCancel)="cancel.emit()"
      (nzOnOk)="handleSubmit()"
    >
      <nz-checkbox-group
        [ngModel]="selectedKeys()"
        (ngModelChange)="selectedKeys.set($event)"
        [nzOptions]="checkboxOptions()"
      ></nz-checkbox-group>
    </nz-modal>
  `,
})
export class ExportColumnSelectorComponent {
  columns = input.required<ColumnOption[]>();
  visible = input(false);

  submit = output<string[]>();
  cancel = output<void>();

  protected readonly selectedKeys = signal<string[]>([]);

  protected readonly checkboxOptions = computed(() =>
    this.columns().map(c => ({
      label: c.label,
      value: c.key,
      checked: c.selected,
    }))
  );

  constructor() {
    effect(() => {
      const initial = this.columns()
        .filter(c => c.selected)
        .map(c => c.key);
      this.selectedKeys.set(initial);
    });
  }

  protected handleSubmit(): void {
    this.submit.emit(this.selectedKeys());
  }
}
```

#### Backend — validación de columnas permitidas

```python
from typing import ClassVar

from pydantic import BaseModel, field_validator, ValidationError


class ExportRequest(BaseModel):
    """DTO para solicitudes de exportación con validación de columnas permitidas."""

    selected_columns: list[str] = []
    language: str = "es"

    ALLOWED_COLUMNS: ClassVar[set[str]] = {
        "EntityId", "Name", "Code", "Status", "RecordCreationDate",
        "Email", "Phone", "Address", "Department", "Role",
    }

    @field_validator("selected_columns", mode="before")
    @classmethod
    def validate_columns(cls, v: list[str]) -> list[str]:
        """Valida que solo se incluyan columnas permitidas (case-insensitive)."""
        columns_lower: set[str] = {col.lower() for col in cls.ALLOWED_COLUMNS}
        invalid: list[str] = [
            col for col in v if col.lower() not in columns_lower
        ]
        if invalid:
            raise ValueError(f"Columnas inválidas: {', '.join(invalid)}")

        if not v:
            # Devolver las primeras 5 columnas por defecto
            return list(cls.ALLOWED_COLUMNS)[:5]

        return v
```

### Column mapping (server-side column name → display name)

El mapeo de nombres técnicos a nombres visibles debe hacerse en el backend con soporte de multi-idioma.

#### Python — Dictionary de mapeo por idioma

```python
from typing import ClassVar


class ColumnMapping:
    """Mapeo de nombres técnicos de columna a nombres visibles por idioma."""

    MAPS: ClassVar[dict[str, dict[str, str]]] = {
        "es": {
            "EntityId": "ID",
            "Name": "Nombre",
            "Code": "Código",
            "Status": "Estado",
            "RecordCreationDate": "Fecha de creación",
            "Email": "Correo electrónico",
            "Phone": "Teléfono",
            "Address": "Dirección",
            "Department": "Departamento",
            "Role": "Rol",
        },
        "en": {
            "EntityId": "ID",
            "Name": "Name",
            "Code": "Code",
            "Status": "Status",
            "RecordCreationDate": "Creation date",
            "Email": "Email",
            "Phone": "Phone",
            "Address": "Address",
            "Department": "Department",
            "Role": "Role",
        },
        "pt": {
            "EntityId": "ID",
            "Name": "Nome",
            "Code": "Código",
            "Status": "Status",
            "RecordCreationDate": "Data de criação",
            "Email": "E-mail",
            "Phone": "Telefone",
            "Address": "Endereço",
            "Department": "Departamento",
            "Role": "Função",
        },
    }

    @classmethod
    def get_header(cls, column_key: str, language: str) -> str:
        """Obtiene el nombre visible de una columna en el idioma solicitado."""
        lang_map: dict[str, str] | None = cls.MAPS.get(language)
        if lang_map:
            header: str | None = lang_map.get(column_key)
            if header:
                return header

        # Fallback a inglés, luego al nombre técnico
        return cls.MAPS.get("en", {}).get(column_key, column_key)

    @classmethod
    def get_mapping(cls, language: str) -> dict[str, str]:
        """Obtiene el diccionario completo de mapeo para un idioma."""
        return cls.MAPS.get(language, cls.MAPS["en"])
```

### i18n para column headers en Excel

En aplicaciones multi-idioma, los encabezados del Excel deben respetar el idioma del usuario que solicita la exportación.

#### Frontend — pasar idioma en la request (React)

```typescript
import i18n from '../../core/i18n/i18n';

async function exportEntities(params: ExportParams): Promise<{ blob: Blob; filename: string }> {
  const query = toQueryString({ ...params, language: i18n.language });
  const res = await fetch(`/api/v1/entities/export?${query}`);
  if (!res.ok) throw new Error('Export failed');

  const disposition = res.headers.get('content-disposition');
  const filenameMatch = disposition?.match(/filename="?(.+?)"?$/);
  const filename = filenameMatch?.[1] || `export_${Date.now()}.xlsx`;

  return { blob: await res.blob(), filename };
}
```

#### Frontend — pasar idioma en la request (Angular)

```typescript
@Injectable({ providedIn: 'root' })
export class ExportService {
  private readonly http = inject(HttpClient);
  private readonly i18n = inject(I18nService);

  exportEntities(params: ExportParams): Observable<{ blob: Blob; filename: string }> {
    return this.http.get('/api/v1/entities/export', {
      params: toHttpParams({
        ...params,
        language: this.i18n.currentLang(),
      }),
      responseType: 'blob',
      observe: 'response',
    }).pipe(
      map(response => {
        const disposition = response.headers.get('content-disposition');
        const filenameMatch = disposition?.match(/filename="?(.+?)"?$/);
        const filename = filenameMatch?.[1] || `export_${Date.now()}.xlsx`;
        return { blob: response.body!, filename };
      })
    );
  }
}
```

#### Java — ResourceBundle para headers

```java
@Component
public class ColumnHeaderResolver {

    private static final Map<String, ResourceBundle> BUNDLES = Map.of(
        "es", ResourceBundle.getBundle("i18n.export-columns", new Locale("es")),
        "en", ResourceBundle.getBundle("i18n.export-columns", new Locale("en")),
        "pt", ResourceBundle.getBundle("i18n.export-columns", new Locale("pt"))
    );

    public String getHeader(String columnKey, String language) {
        ResourceBundle bundle = BUNDLES.getOrDefault(language, BUNDLES.get("en"));
        try {
            return bundle.getString("column." + columnKey);
        } catch (MissingResourceException e) {
            return columnKey;
        }
    }
}
```

#### Archivos de propiedades i18n

```properties
# i18n/export-columns_es.properties
column.EntityId = ID
column.Name = Nombre
column.Code = Código
column.Status = Estado
column.RecordCreationDate = Fecha de creación
column.Email = Correo electrónico
column.Phone = Teléfono
column.Address = Dirección
column.Department = Departamento
column.Role = Rol
```

```properties
# i18n/export-columns_en.properties
column.EntityId = ID
column.Name = Name
column.Code = Code
column.Status = Status
column.RecordCreationDate = Creation date
column.Email = Email
column.Phone = Phone
column.Address = Address
column.Department = Department
column.Role = Role
```

### Multi-language support en el archivo exportado

Para reportes que serán compartidos entre usuarios de diferentes idiomas, se puede incluir el encabezado en múltiples idiomas o generar una leyenda de traducciones.

#### Hoja adicional de traducciones

```python
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter


def add_translation_sheet(
    workbook: Workbook,
    source_language: str,
    columns: list[str],
) -> None:
    """Agrega una hoja con traducciones de encabezados en múltiples idiomas."""
    sheet = workbook.create_sheet("Traducciones")

    # Headers de la hoja de traducciones
    bold_font: Font = Font(bold=True)
    headers: list[str] = ["Columna", "Español", "English", "Português"]
    for col_idx, header_text in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_idx, value=header_text)
        cell.font = bold_font

    # Filas de traducción
    row: int = 2
    for col in columns:
        sheet.cell(row=row, column=1, value=col)
        sheet.cell(row=row, column=2, value=ColumnMapping.get_header(col, "es"))
        sheet.cell(row=row, column=3, value=ColumnMapping.get_header(col, "en"))
        sheet.cell(row=row, column=4, value=ColumnMapping.get_header(col, "pt"))
        row += 1

    # Autoajuste de columnas
    for col_idx in range(1, 5):
        sheet.column_dimensions[get_column_letter(col_idx)].auto_size = True
```

#### Formato condicional en el Excel

Para mejorar la legibilidad, aplicar formato condicional a celdas específicas según su contenido.

```python
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet


def apply_conditional_formatting(
    sheet: Worksheet,
    total_rows: int,
    total_columns: int,
) -> None:
    """Aplica formato condicional para mejorar legibilidad del Excel."""

    # Rango de datos (sin incluir header)
    range_str: str = f"A2:{get_column_letter(total_columns)}{total_rows}"

    # Alternar colores de fila (gris claro en filas pares)
    gray_fill: PatternFill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
    sheet.conditional_formatting.add(
        range_str,
        CellIsRule(
            operator="equal",
            formula=["MOD(ROW(),2)"],
            fill=gray_fill,
        ),
    )

    # Resaltar valores negativos en rojo (asumiendo columna numérica)
    red_font: Font = Font(color="FF0000")
    sheet.conditional_formatting.add(
        range_str,
        CellIsRule(
            operator="lessThan",
            formula=["0"],
            font=red_font,
        ),
    )

    # Columna de estado (columna 3): colores según valor
    status_range: str = f"C2:C{total_rows}"
    green_fill: PatternFill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    green_font: Font = Font(color="006100")
    red_fill: PatternFill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    dark_red_font: Font = Font(color="9C0006")
    yellow_fill: PatternFill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
    brown_font: Font = Font(color="9C6500")

    sheet.conditional_formatting.add(
        status_range,
        CellIsRule(operator="equal", formula=['"Activo"'], fill=green_fill, font=green_font),
    )
    sheet.conditional_formatting.add(
        status_range,
        CellIsRule(operator="equal", formula=['"Inactivo"'], fill=red_fill, font=dark_red_font),
    )
    sheet.conditional_formatting.add(
        status_range,
        CellIsRule(operator="equal", formula=['"Pendiente"'], fill=yellow_fill, font=brown_font),
    )
```

#### Congelar encabezados (freeze panes)

```python
# Congelar la primera fila (headers) para que siempre sea visible al hacer scroll
sheet.freeze_panes = "A2"

# Congelar también la primera columna si el ID debe ser visible siempre
sheet.freeze_panes = "B2"
```

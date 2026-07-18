# API Specification: {ModuleName}

## 1. Scope

### Included
- {included functionality}

### Excluded
- {excluded functionality}

## 2. Data Model

```mermaid
erDiagram
    {Entity1} ||--o{ {Entity2} : "has"
    {Entity1} {
        int Id PK
        string Name
        string Status
    }
    {Entity2} {
        int Id PK
        int {Entity1}Id FK
        string Description
    }
```

### Tables

| Entity | Description | Key Fields |
|--------|-------------|------------|
| `{Entity1}` | {description} | `{Entity1}Id` (PK), `Name`, `Status` |
| `{Entity2}` | {description} | `{Entity2}Id` (PK), `{Entity1}Id` (FK), `Description` |

## 3. Required Catalogs

| Code | Name | Description |
|------|------|-------------|
| `{STATUS_XXX}` | {value} | {description} |

## 4. State Flow

| Current State | Action | Next State | Conditions |
|---------------|--------|------------|------------|
| {state1} | {action} | {state2} | {condition} |

## 5. REST Endpoints

### {Entity1}

#### `GET /api/v1/{entities}` — List {Entity1}

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `page` | int | No | Page number (default: 1) |
| `pageSize` | int | No | Items per page (default: 20) |
| `sortBy` | string | No | Sort column |
| `sortOrder` | string | No | ASC/DESC |

**Response `200`:**

```json
{
  "data": {
    "items": [{ "id": 1, "name": "...", "status": "..." }],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "totalRecords": 50,
      "totalPages": 3
    }
  }
}
```

| DB Object | Type | Description |
|-----------|------|-------------|
| `{Schema}.List{Entity1}` | SP | Paginated list |

#### `GET /api/v1/{entities}/{id}` — Get {Entity1}

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | int | Yes | Entity ID |

**Response `200`:**

```json
{
  "data": {
    "id": 1,
    "name": "...",
    "status": "...",
    "createdDate": "2025-01-01T00:00:00Z"
  }
}
```

**Errors:** `{MOD}_001` — Not found

#### `POST /api/v1/{entities}` — Create {Entity1}

**Request:**

```json
{
  "name": "string (required, max 500)",
  "status": "string (catalog)"
}
```

**Response `201`:**

```json
{
  "data": { "id": 1, "name": "...", "status": "..." }
}
```

| DB Object | Type | Description |
|-----------|------|-------------|
| `{Schema}.Create{Entity1}` | SP | Insert record |

#### `PUT /api/v1/{entities}/{id}` — Update {Entity1}

**Request:**

```json
{
  "name": "string (max 500)",
  "status": "string (catalog)"
}
```

**Response `200`:** Returns updated record

#### `DELETE /api/v1/{entities}/{id}` — Delete {Entity1}

**Response `200`:**

```json
{
  "data": { "result": true }
}
```

### {Entity2} — Sub-entity under {Entity1}

#### `GET /api/v1/{entities}/{entity1Id}/{subEntities}` — List {Entity2}

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `entity1Id` | int | Yes | Parent entity ID |

## 6. Database Objects

| Endpoint | SP/Query | Parameters |
|----------|----------|------------|
| List {Entity1} | `{Schema}.List{Entity1}` | `@Page`, `@PageSize`, `@SortBy`, `@SortOrder` |
| Get {Entity1} | `{Schema}.Get{Entity1}` | `@Id` |
| Create {Entity1} | `{Schema}.Create{Entity1}` | `@Name`, `@Status`, `@CurrentUser` |
| Update {Entity1} | `{Schema}.Update{Entity1}` | `@Id`, `@Name`, `@Status`, `@CurrentUser` |
| Delete {Entity1} | `{Schema}.Delete{Entity1}` | `@Id`, `@CurrentUser` |

## 7. Shared DTOs

### Pagination

```json
{
  "page": 1,
  "pageSize": 20,
  "totalRecords": 100,
  "totalPages": 5
}
```

### ApiResponse

```json
{
  "data": {},
  "success": true,
  "message": null
}
```

## 8. Business Rules

| ID | Rule | Category |
|----|------|----------|
| `BUS_001` | {description} | Validation |
| `BUS_002` | {description} | State |

## 9. Error Codes

| Code | HTTP | Message | When |
|------|------|---------|------|
| `VAL_001` | 400 | {Field} is required | Required field missing |
| `VAL_008` | 400 | {Field} max length exceeded | Field too long |
| `{MOD}_001` | 404 | {Entity} not found | Invalid ID |
| `{MOD}_002` | 409 | Duplicate {field} | Unique constraint |
| `{MOD}_003` | 422 | Cannot {action} in {state} | State transition denied |

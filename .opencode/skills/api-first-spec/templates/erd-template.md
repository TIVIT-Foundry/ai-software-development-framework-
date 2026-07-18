# Entity-Relationship Diagram: {ModuleName}

## Mermaid ERD

```mermaid
erDiagram
    {Entity1} ||--o{ {Entity2} : "has"
    {Entity1} ||--o{ {Entity3} : "has"
    {Entity2} }o--|| {Catalog1} : "references"
    {Entity1} {
        int {Entity1}Id PK
        string Name
        string Code UK
        string Status
        int CreatedBy
        datetime CreatedDate
        int? UpdatedBy
        datetime? UpdatedDate
    }
    {Entity2} {
        int {Entity2}Id PK
        int {Entity1}Id FK
        string Description
        int {Catalog1}Id FK
        string RecordStatus
        int CreatedBy
        datetime CreatedDate
    }
    {Entity3} {
        int {Entity3}Id PK
        int {Entity1}Id FK
        decimal Amount
        date EffectiveDate
    }
    {Catalog1} {
        int {Catalog1}Id PK
        string Name
        string Value UK
        int SortOrder
    }
```

## Entity Descriptions

| Entity | Type | Description | Cardinality | Audit |
|--------|------|-------------|-------------|-------|
| `{Entity1}` | Main | {description} | Parent of {Entity2} | Yes |
| `{Entity2}` | Detail | {description} | Child of {Entity1} | Yes |
| `{Entity3}` | Detail | {description} | Child of {Entity1} | Yes |
| `{Catalog1}` | Catalog | {description} | Referenced by {Entity2} | No |

## Column Details

### {Entity1}

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `{entity1}_id` | `SERIAL` | No | — | Primary key |
| `name` | `VARCHAR(500)` | No | — | Entity name |
| `code` | `VARCHAR(50)` | No | — | Unique code |
| `status` | `VARCHAR(20)` | No | `'DRAFT'` | Current status |
| `created_by` | `INT` | No | — | User who created |
| `created_date` | `TIMESTAMPTZ` | No | `NOW()` | Creation timestamp |
| `updated_by` | `INT` | Yes | — | Last modifier |
| `updated_date` | `TIMESTAMPTZ` | Yes | — | Last modification |

### {Entity2}

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `{entity2}_id` | `SERIAL` | No | — | Primary key |
| `{entity1}_id` | `INT` | No | — | FK to {Entity1} |
| `description` | `VARCHAR(1000)` | No | — | Detail description |
| `{catalog1}_id` | `INT` | No | — | FK to {Catalog1} |
| `record_status` | `CHAR(1)` | No | `'A'` | A=Active, I=Inactive |
| `created_by` | `INT` | No | — | User who created |
| `created_date` | `TIMESTAMPTZ` | No | `NOW()` | Creation timestamp |

### {Catalog1}

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `{catalog1}_id` | `SERIAL` | No | — | Primary key |
| `name` | `VARCHAR(200)` | No | — | Display name |
| `value` | `VARCHAR(50)` | No | — | Unique code value |
| `sort_order` | `INT` | No | `0` | Display order |

## Indexes

| Table | Index | Columns | Unique | Description |
|-------|-------|---------|--------|-------------|
| `{entity1}` | `ix_{entity1}_code` | `code` | Yes | Unique code lookup |
| `{entity1}` | `ix_{entity1}_status` | `status` | No | Status filtering |
| `{entity2}` | `ix_{entity2}_{entity1}_id` | `{entity1}_id` | No | Parent lookup |

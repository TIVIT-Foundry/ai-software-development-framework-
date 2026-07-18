# Module: Task Management

> Spec for a task management module using the Framework Agéntico.

## Entity / ERD

### Task

| Field | Type | Description |
|-------|------|-------------|
| Id | int | Primary key, auto-increment |
| Title | string | Task title, required, max 200 chars |
| Description | string? | Optional description, max 1000 chars |
| Status | enum | Pending, InProgress, Completed, Cancelled |
| Priority | enum | Low, Medium, High, Critical |
| DueDate | datetime? | Optional due date |
| AssignedTo | int? | User ID assigned to the task |
| CreatedDate | datetime | Auto-generated on creation |
| UpdatedDate | datetime? | Auto-generated on update |
| CreatedBy | int | User ID who created the task |
| RecordStatus | string | A = Active, I = Inactive |

### Category

| Field | Type | Description |
|-------|------|-------------|
| Id | int | Primary key, auto-increment |
| Name | string | Category name, required, max 100 chars |
| Color | string? | Hex color code for UI display |
| CreatedDate | datetime | Auto-generated |
| RecordStatus | string | A = Active, I = Inactive |

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/tasks | Paginated list of tasks |
| GET | /api/tasks/{id} | Get task by ID |
| POST | /api/tasks | Create a new task |
| PUT | /api/tasks/{id} | Update an existing task |
| DELETE | /api/tasks/{id} | Soft delete a task |
| GET | /api/categories | List all categories |
| GET | /api/categories/{id} | Get category by ID |
| POST | /api/categories | Create a category |
| PUT | /api/categories/{id} | Update a category |
| DELETE | /api/categories/{id} | Delete a category |

## DTOs / Types

### CreateTaskRequest

| Field | Type | Required |
|-------|------|----------|
| Title | string | Yes |
| Description | string | No |
| Status | string | No |
| Priority | string | No |
| DueDate | datetime | No |
| AssignedTo | int | No |

### UpdateTaskRequest

| Field | Type | Required |
|-------|------|----------|
| Title | string | No |
| Description | string | No |
| Status | string | No |
| Priority | string | No |
| DueDate | datetime | No |
| AssignedTo | int | No |

### TaskResponse

| Field | Type |
|-------|------|
| Id | int |
| Title | string |
| Description | string |
| Status | string |
| Priority | string |
| DueDate | datetime |
| AssignedTo | int |
| CreatedDate | datetime |
| UpdatedDate | datetime |
| CreatedBy | int |

## Business Rules

1. Title is required and must not exceed 200 characters.
2. Description is optional and must not exceed 1000 characters.
3. Status transitions: Pending → InProgress → Completed; any state → Cancelled.
4. Soft delete sets RecordStatus to 'I' instead of physical deletion.
5. Only active records (RecordStatus = 'A') appear in lists.

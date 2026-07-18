/* ============================================================
   SP: {Schema}.Create{Entity}
   Description: Creates a new {Entity} record
   Author: Framework Generated
   Version: 1.0
   CHANGE HISTORY:
   | Version | Date | Author | Change |
   |---------|------|--------|--------|
   | 1.0 | {DATE} | {AUTHOR} | Initial version |
   ============================================================ */
CREATE OR ALTER PROCEDURE {Schema}.Create{Entity}
    @ParamIName NVARCHAR(500),
    @ParamICode NVARCHAR(50),
    @ParamIStatus NVARCHAR(20) = 'DRAFT',
    @ParamICurrentUserId INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        ---------------------------------------------------------------
        -- STEP 1: Validations
        ---------------------------------------------------------------
        IF @ParamIName IS NULL OR LTRIM(RTRIM(@ParamIName)) = ''
        BEGIN
            SELECT 'VAL_001' AS ErrorCode, 'Name' AS Field, 'Name is required' AS Message;
            RETURN;
        END

        IF LEN(@ParamIName) > 500
        BEGIN
            SELECT 'VAL_008' AS ErrorCode, 'Name' AS Field, 'Name max length is 500' AS Message;
            RETURN;
        END

        IF EXISTS (SELECT 1 FROM {Schema}.{Entity} WITH(NOLOCK) WHERE Code = @ParamICode AND RecordStatus = 'A')
        BEGIN
            SELECT '{MOD}_002' AS ErrorCode, 'Code' AS Field, 'Code already exists' AS Message;
            RETURN;
        END

        ---------------------------------------------------------------
        -- STEP 2: Insert
        ---------------------------------------------------------------
        INSERT INTO {Schema}.{Entity} (
            Name,
            Code,
            Status,
            CreatedBy,
            CreatedDate
        ) VALUES (
            LTRIM(RTRIM(@ParamIName)),
            LTRIM(RTRIM(@ParamICode)),
            @ParamIStatus,
            @ParamICurrentUserId,
            GETUTCDATE()
        );

        DECLARE @VNewId INT = SCOPE_IDENTITY();

        ---------------------------------------------------------------
        -- STEP 3: Return created record
        ---------------------------------------------------------------
        SELECT
            e.{Entity}Id,
            e.Name,
            e.Code,
            e.Status,
            e.CreatedBy,
            e.CreatedDate,
            e.UpdatedBy,
            e.UpdatedDate
        FROM {Schema}.{Entity} e WITH(NOLOCK)
        WHERE e.{Entity}Id = @VNewId;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        EXEC Log.GetErrorInfo;
    END CATCH
END;
GO

/* ============================================================
   SP: {Schema}.Get{Entity}
   Description: Gets a {Entity} by ID
   ============================================================ */
CREATE OR ALTER PROCEDURE {Schema}.Get{Entity}
    @ParamIId INT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        SELECT
            e.{Entity}Id,
            e.Name,
            e.Code,
            e.Status,
            e.CreatedBy,
            e.CreatedDate,
            e.UpdatedBy,
            e.UpdatedDate
        FROM {Schema}.{Entity} e WITH(NOLOCK)
        WHERE e.{Entity}Id = @ParamIId AND e.RecordStatus = 'A';

        IF @@ROWCOUNT = 0
        BEGIN
            SELECT '{MOD}_001' AS ErrorCode, 'Id' AS Field, '{Entity} not found' AS Message;
            RETURN;
        END
    END TRY
    BEGIN CATCH
        EXEC Log.GetErrorInfo;
    END CATCH
END;
GO

/* ============================================================
   SP: {Schema}.Update{Entity}
   Description: Updates an existing {Entity} record
   ============================================================ */
CREATE OR ALTER PROCEDURE {Schema}.Update{Entity}
    @ParamIId INT,
    @ParamIName NVARCHAR(500) = NULL,
    @ParamICode NVARCHAR(50) = NULL,
    @ParamIStatus NVARCHAR(20) = NULL,
    @ParamICurrentUserId INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        ---------------------------------------------------------------
        -- STEP 1: Validate existence
        ---------------------------------------------------------------
        IF NOT EXISTS (SELECT 1 FROM {Schema}.{Entity} WITH(NOLOCK) WHERE {Entity}Id = @ParamIId AND RecordStatus = 'A')
        BEGIN
            SELECT '{MOD}_001' AS ErrorCode, 'Id' AS Field, '{Entity} not found' AS Message;
            RETURN;
        END

        ---------------------------------------------------------------
        -- STEP 2: Update
        ---------------------------------------------------------------
        UPDATE {Schema}.{Entity}
        SET
            Name = COALESCE(NULLIF(LTRIM(RTRIM(@ParamIName)), ''), Name),
            Code = COALESCE(NULLIF(LTRIM(RTRIM(@ParamICode)), ''), Code),
            Status = COALESCE(@ParamIStatus, Status),
            UpdatedBy = @ParamICurrentUserId,
            UpdatedDate = GETUTCDATE()
        WHERE {Entity}Id = @ParamIId;

        ---------------------------------------------------------------
        -- STEP 3: Return updated record
        ---------------------------------------------------------------
        SELECT
            e.{Entity}Id,
            e.Name,
            e.Code,
            e.Status,
            e.CreatedBy,
            e.CreatedDate,
            e.UpdatedBy,
            e.UpdatedDate
        FROM {Schema}.{Entity} e WITH(NOLOCK)
        WHERE e.{Entity}Id = @ParamIId;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        EXEC Log.GetErrorInfo;
    END CATCH
END;
GO

/* ============================================================
   SP: {Schema}.Delete{Entity}
   Description: Soft deletes a {Entity} record
   ============================================================ */
CREATE OR ALTER PROCEDURE {Schema}.Delete{Entity}
    @ParamIId INT,
    @ParamICurrentUserId INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM {Schema}.{Entity} WITH(NOLOCK) WHERE {Entity}Id = @ParamIId AND RecordStatus = 'A')
        BEGIN
            SELECT '{MOD}_001' AS ErrorCode, 'Id' AS Field, '{Entity} not found' AS Message;
            RETURN;
        END

        UPDATE {Schema}.{Entity}
        SET
            RecordStatus = 'I',
            UpdatedBy = @ParamICurrentUserId,
            UpdatedDate = GETUTCDATE()
        WHERE {Entity}Id = @ParamIId;

        SELECT 1 AS Result;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        EXEC Log.GetErrorInfo;
    END CATCH
END;
GO

/* ============================================================
   SP: {Schema}.List{Entity}
   Description: Paginated list of {Entity} records
   ============================================================ */
CREATE OR ALTER PROCEDURE {Schema}.List{Entity}
    @ParamIPage INT = 1,
    @ParamIPageSize INT = 20,
    @ParamISortBy NVARCHAR(50) = 'CreatedDate',
    @ParamISortOrder NVARCHAR(4) = 'DESC',
    @ParamISearchFilter NVARCHAR(100) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        DECLARE @VSearchPattern NVARCHAR(102) = NULL;
        DECLARE @VAllowedColumns NVARCHAR(MAX) = 'CreatedDate,Name,Code,Status';

        IF @ParamISearchFilter IS NOT NULL AND LTRIM(RTRIM(@ParamISearchFilter)) <> ''
            SET @VSearchPattern = '%' + LTRIM(RTRIM(@ParamISearchFilter)) + '%';

        IF @ParamISortBy NOT IN (SELECT [value] FROM STRING_SPLIT(@VAllowedColumns, ','))
            SET @ParamISortBy = 'CreatedDate';
        IF @ParamISortOrder NOT IN ('ASC', 'DESC')
            SET @ParamISortOrder = 'DESC';

        SELECT
            e.{Entity}Id,
            e.Name,
            e.Code,
            e.Status,
            e.CreatedBy,
            e.CreatedDate,
            e.UpdatedBy,
            e.UpdatedDate,
            COUNT(*) OVER() AS TotalCount
        FROM {Schema}.{Entity} e WITH(NOLOCK)
        WHERE e.RecordStatus = 'A'
            AND (@VSearchPattern IS NULL
                OR e.Name LIKE @VSearchPattern
                OR e.Code LIKE @VSearchPattern)
        ORDER BY
            CASE WHEN @ParamISortOrder = 'ASC' THEN
                CASE @ParamISortBy
                    WHEN 'CreatedDate' THEN CONVERT(NVARCHAR(50), e.CreatedDate, 126)
                    WHEN 'Name' THEN e.Name
                    WHEN 'Code' THEN e.Code
                    WHEN 'Status' THEN e.Status
                END
            END ASC,
            CASE WHEN @ParamISortOrder = 'DESC' THEN
                CASE @ParamISortBy
                    WHEN 'CreatedDate' THEN CONVERT(NVARCHAR(50), e.CreatedDate, 126)
                    WHEN 'Name' THEN e.Name
                    WHEN 'Code' THEN e.Code
                    WHEN 'Status' THEN e.Status
                END
            END DESC
        OFFSET (@ParamIPage - 1) * @ParamIPageSize ROWS
        FETCH NEXT @ParamIPageSize ROWS ONLY;
    END TRY
    BEGIN CATCH
        EXEC Log.GetErrorInfo;
    END CATCH
END;
GO

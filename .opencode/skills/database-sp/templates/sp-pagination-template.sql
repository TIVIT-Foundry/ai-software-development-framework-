/* ============================================================
   SP: {Schema}.List{Entity}
   Description: Paginated list with safe sorting
   Author: Framework Generated
   Version: 1.0
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
        ---------------------------------------------------------------
        -- STEP 1: Variables
        ---------------------------------------------------------------
        DECLARE @VSearchPattern NVARCHAR(102) = NULL;
        DECLARE @VAllowedColumns NVARCHAR(MAX) = 'CreatedDate,Name,Code,Status,Priority';

        ---------------------------------------------------------------
        -- STEP 2: Search filter
        ---------------------------------------------------------------
        IF @ParamISearchFilter IS NOT NULL AND LTRIM(RTRIM(@ParamISearchFilter)) <> ''
            SET @VSearchPattern = '%' + LTRIM(RTRIM(@ParamISearchFilter)) + '%';

        ---------------------------------------------------------------
        -- STEP 3: Safe sorting (whitelist)
        ---------------------------------------------------------------
        IF @ParamISortBy NOT IN (SELECT [value] FROM STRING_SPLIT(@VAllowedColumns, ','))
            SET @ParamISortBy = 'CreatedDate';
        IF @ParamISortOrder NOT IN ('ASC', 'DESC')
            SET @ParamISortOrder = 'DESC';

        ---------------------------------------------------------------
        -- STEP 4: Paginated query with TotalCount
        ---------------------------------------------------------------
        SELECT
            e.{Entity}Id,
            e.Name,
            e.Code,
            e.Status,
            e.CreatedDate,
            e.UpdatedDate,
            COUNT(*) OVER() AS TotalCount
        FROM {Schema}.{Entity} e WITH(NOLOCK)
        WHERE e.RecordStatus = 'A'
            AND (@VSearchPattern IS NULL
                OR e.Name LIKE @VSearchPattern
                OR e.Code LIKE @VSearchPattern
                OR e.Status LIKE @VSearchPattern)
        ORDER BY
            CASE WHEN @ParamISortOrder = 'ASC' THEN
                CASE @ParamISortBy
                    WHEN 'CreatedDate' THEN CONVERT(NVARCHAR(50), e.CreatedDate, 126)
                    WHEN 'Name' THEN e.Name
                    WHEN 'Code' THEN e.Code
                    WHEN 'Status' THEN e.Status
                    WHEN 'Priority' THEN e.Priority
                END
            END ASC,
            CASE WHEN @ParamISortOrder = 'DESC' THEN
                CASE @ParamISortBy
                    WHEN 'CreatedDate' THEN CONVERT(NVARCHAR(50), e.CreatedDate, 126)
                    WHEN 'Name' THEN e.Name
                    WHEN 'Code' THEN e.Code
                    WHEN 'Status' THEN e.Status
                    WHEN 'Priority' THEN e.Priority
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

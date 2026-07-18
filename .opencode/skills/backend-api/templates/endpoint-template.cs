using Microsoft.AspNetCore.Http.HttpResults;
using {Namespace}.Shared;

namespace {Namespace}.Modules.{Module}.Features.List{Entity};

public static class List{Entity}Endpoint
{
    public static void Map(IEndpointRouteBuilder app)
    {
        app.MapGet("/", Handle)
            .Produces<ApiResponse<PaginatedResult<List{Entity}Response>>>(200)
            .ProducesValidationProblem()
            .WithSummary("List {Entity}")
            .WithDescription("Returns a paginated list of {Entity} records");
    }

    private static async Task<IResult> Handle(
        [AsParameters] List{Entity}Request request,
        [FromServices] List{Entity}Handler handler,
        [FromServices] HeaderToken headerToken,
        CancellationToken ct)
    {
        var currentUser = headerToken?.EmployeeId
            ?? throw new UnauthorizedAccessException();

        var (items, pagination) = await handler.HandleAsync(request, ct);

        return Results.Ok(ApiResponse<PaginatedResult<List{Entity}Response>>.Ok(
            new PaginatedResult<List{Entity}Response>(items, pagination)));
    }
}

public static class Get{Entity}Endpoint
{
    public static void Map(IEndpointRouteBuilder app)
    {
        app.MapGet("/{id:int}", Handle)
            .Produces<ApiResponse<Get{Entity}Response>>(200)
            .Produces<ApiError>(404)
            .WithSummary("Get {Entity} by ID");
    }

    private static async Task<IResult> Handle(
        int id,
        [FromServices] Get{Entity}Handler handler,
        [FromServices] HeaderToken headerToken,
        CancellationToken ct)
    {
        _ = headerToken?.EmployeeId
            ?? throw new UnauthorizedAccessException();

        var result = await handler.HandleAsync(id, ct);
        return Results.Ok(ApiResponse<Get{Entity}Response>.Ok(result));
    }
}

public static class Create{Entity}Endpoint
{
    public static void Map(IEndpointRouteBuilder app)
    {
        app.MapPost("/", Handle)
            .Produces<ApiResponse<Create{Entity}Response>>(201)
            .ProducesValidationProblem()
            .WithSummary("Create {Entity}");
    }

    private static async Task<IResult> Handle(
        Create{Entity}Request request,
        [FromServices] Create{Entity}Handler handler,
        [FromServices] HeaderToken headerToken,
        CancellationToken ct)
    {
        var currentUser = headerToken?.EmployeeId
            ?? throw new UnauthorizedAccessException();

        var result = await handler.HandleAsync(request, currentUser, ct);
        return Results.Created($"/api/v1/{result.Id}", ApiResponse<Create{Entity}Response>.Ok(result));
    }
}

public static class Update{Entity}Endpoint
{
    public static void Map(IEndpointRouteBuilder app)
    {
        app.MapPut("/{id:int}", Handle)
            .Produces<ApiResponse<Update{Entity}Response>>(200)
            .ProducesValidationProblem()
            .WithSummary("Update {Entity}");
    }

    private static async Task<IResult> Handle(
        int id,
        Update{Entity}Request request,
        [FromServices] Update{Entity}Handler handler,
        [FromServices] HeaderToken headerToken,
        CancellationToken ct)
    {
        var currentUser = headerToken?.EmployeeId
            ?? throw new UnauthorizedAccessException();

        var result = await handler.HandleAsync(id, request, currentUser, ct);
        return Results.Ok(ApiResponse<Update{Entity}Response>.Ok(result));
    }
}

public static class Delete{Entity}Endpoint
{
    public static void Map(IEndpointRouteBuilder app)
    {
        app.MapDelete("/{id:int}", Handle)
            .Produces<ApiResponse<bool>>(200)
            .WithSummary("Delete {Entity}");
    }

    private static async Task<IResult> Handle(
        int id,
        [FromServices] Delete{Entity}Handler handler,
        [FromServices] HeaderToken headerToken,
        CancellationToken ct)
    {
        var currentUser = headerToken?.EmployeeId
            ?? throw new UnauthorizedAccessException();

        var result = await handler.HandleAsync(id, currentUser, ct);
        return Results.Ok(ApiResponse<bool>.Ok(result));
    }
}

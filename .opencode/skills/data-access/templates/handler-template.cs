using Dapper;
using System.Data;

namespace {Namespace}.Modules.{Module}.Features.{Entity};

public class List{Entity}Handler(IDbConnection db)
{
    public async Task<(List<{Entity}ListItem>, PaginationResult)> HandleAsync(
        List{Entity}Request request,
        CancellationToken ct = default)
    {
        var command = new CommandDefinition(
            "{Schema}.List{Entity}",
            new
            {
                ParamIPage = request.Page,
                ParamIPageSize = request.PageSize,
                ParamISortBy = request.SortBy ?? "CreatedDate",
                ParamISortOrder = request.SortOrder ?? "DESC",
                ParamISearchFilter = request.SearchFilter
            },
            commandType: CommandType.StoredProcedure,
            cancellationToken: ct);

        var results = await db.QueryAsync<dynamic>(command);
        var items = new List<{Entity}ListItem>();
        int totalCount = 0;

        foreach (var row in results)
        {
            var dict = (IDictionary<string, object>)row;
            SpResultHelper.ThrowIfError(dict);

            totalCount = dict.GetValue<int>("TotalCount");
            items.Add(new {Entity}ListItem
            {
                Id = dict.GetValue<int>("{Entity}Id"),
                Name = dict.GetValue<string>("Name") ?? string.Empty,
                Code = dict.GetValue<string>("Code") ?? string.Empty,
                Status = dict.GetValue<string>("Status") ?? string.Empty,
                CreatedDate = dict.GetValue<DateTime>("CreatedDate"),
            });
        }

        var pagination = new PaginationResult(
            request.Page,
            request.PageSize,
            totalCount);

        return (items, pagination);
    }
}

public class Get{Entity}Handler(IDbConnection db)
{
    public async Task<Get{Entity}Response> HandleAsync(
        int id,
        CancellationToken ct = default)
    {
        var command = new CommandDefinition(
            "{Schema}.Get{Entity}",
            new { ParamIId = id },
            commandType: CommandType.StoredProcedure,
            cancellationToken: ct);

        var result = await db.QuerySingleAsync<dynamic>(command);
        SpResultHelper.ThrowIfError((IDictionary<string, object>)result);

        var dict = (IDictionary<string, object>)result;
        return new Get{Entity}Response
        {
            Id = dict.GetValue<int>("{Entity}Id"),
            Name = dict.GetValue<string>("Name") ?? string.Empty,
            Code = dict.GetValue<string>("Code") ?? string.Empty,
            Status = dict.GetValue<string>("Status") ?? string.Empty,
            CreatedBy = dict.GetValue<int>("CreatedBy"),
            CreatedDate = dict.GetValue<DateTime>("CreatedDate"),
            UpdatedBy = dict.GetValue<int?>("UpdatedBy"),
            UpdatedDate = dict.GetValue<DateTime?>("UpdatedDate"),
        };
    }
}

public class Create{Entity}Handler(IDbConnection db)
{
    public async Task<Create{Entity}Response> HandleAsync(
        Create{Entity}Request request,
        int currentUserId,
        CancellationToken ct = default)
    {
        var command = new CommandDefinition(
            "{Schema}.Create{Entity}",
            new
            {
                ParamIName = request.Name,
                ParamICode = request.Code,
                ParamIStatus = request.Status,
                ParamICurrentUserId = currentUserId
            },
            commandType: CommandType.StoredProcedure,
            cancellationToken: ct);

        var result = await db.QuerySingleAsync<dynamic>(command);
        SpResultHelper.ThrowIfError((IDictionary<string, object>)result);

        var dict = (IDictionary<string, object>)result;
        return new Create{Entity}Response
        {
            Id = dict.GetValue<int>("{Entity}Id"),
            Name = dict.GetValue<string>("Name") ?? string.Empty,
            Code = dict.GetValue<string>("Code") ?? string.Empty,
            Status = dict.GetValue<string>("Status") ?? string.Empty,
        };
    }
}

public class Update{Entity}Handler(IDbConnection db)
{
    public async Task<Update{Entity}Response> HandleAsync(
        int id,
        Update{Entity}Request request,
        int currentUserId,
        CancellationToken ct = default)
    {
        var command = new CommandDefinition(
            "{Schema}.Update{Entity}",
            new
            {
                ParamIId = id,
                ParamIName = request.Name,
                ParamICode = request.Code,
                ParamIStatus = request.Status,
                ParamICurrentUserId = currentUserId
            },
            commandType: CommandType.StoredProcedure,
            cancellationToken: ct);

        var result = await db.QuerySingleAsync<dynamic>(command);
        SpResultHelper.ThrowIfError((IDictionary<string, object>)result);

        var dict = (IDictionary<string, object>)result;
        return new Update{Entity}Response
        {
            Id = dict.GetValue<int>("{Entity}Id"),
            Name = dict.GetValue<string>("Name") ?? string.Empty,
            Status = dict.GetValue<string>("Status") ?? string.Empty,
        };
    }
}

public class Delete{Entity}Handler(IDbConnection db)
{
    public async Task<bool> HandleAsync(
        int id,
        int currentUserId,
        CancellationToken ct = default)
    {
        var command = new CommandDefinition(
            "{Schema}.Delete{Entity}",
            new
            {
                ParamIId = id,
                ParamICurrentUserId = currentUserId
            },
            commandType: CommandType.StoredProcedure,
            cancellationToken: ct);

        var result = await db.QueryAsync<dynamic>(command);
        var first = result.FirstOrDefault();
        if (first != null)
        {
            SpResultHelper.ThrowIfError((IDictionary<string, object>)first);
        }
        return true;
    }
}

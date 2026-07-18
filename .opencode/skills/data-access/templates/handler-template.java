package {package}.{module}.repository;

import {package}.{module}.dto.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.core.SqlParameter;
import org.springframework.jdbc.core.simple.SimpleJdbcCall;
import org.springframework.stereotype.Repository;

import javax.annotation.PostConstruct;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@Repository
public class {Entity}Repository {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    private SimpleJdbcCall listProc;
    private SimpleJdbcCall getProc;
    private SimpleJdbcCall createProc;
    private SimpleJdbcCall updateProc;
    private SimpleJdbcCall deleteProc;

    @PostConstruct
    public void init() {
        listProc = new SimpleJdbcCall(jdbcTemplate)
            .withProcedureName("List{Entity}")
            .withSchemaName("{Schema}")
            .declareParameters(
                new SqlParameter("ParamIPage", Types.INTEGER),
                new SqlParameter("ParamIPageSize", Types.INTEGER),
                new SqlParameter("ParamISortBy", Types.VARCHAR),
                new SqlParameter("ParamISortOrder", Types.VARCHAR),
                new SqlParameter("ParamISearchFilter", Types.VARCHAR));

        getProc = new SimpleJdbcCall(jdbcTemplate)
            .withProcedureName("Get{Entity}")
            .withSchemaName("{Schema}")
            .declareParameters(
                new SqlParameter("ParamIId", Types.INTEGER));

        createProc = new SimpleJdbcCall(jdbcTemplate)
            .withProcedureName("Create{Entity}")
            .withSchemaName("{Schema}")
            .declareParameters(
                new SqlParameter("ParamIName", Types.VARCHAR),
                new SqlParameter("ParamICode", Types.VARCHAR),
                new SqlParameter("ParamIStatus", Types.VARCHAR),
                new SqlParameter("ParamICurrentUserId", Types.INTEGER));

        updateProc = new SimpleJdbcCall(jdbcTemplate)
            .withProcedureName("Update{Entity}")
            .withSchemaName("{Schema}")
            .declareParameters(
                new SqlParameter("ParamIId", Types.INTEGER),
                new SqlParameter("ParamIName", Types.VARCHAR),
                new SqlParameter("ParamICode", Types.VARCHAR),
                new SqlParameter("ParamIStatus", Types.VARCHAR),
                new SqlParameter("ParamICurrentUserId", Types.INTEGER));

        deleteProc = new SimpleJdbcCall(jdbcTemplate)
            .withProcedureName("Delete{Entity}")
            .withSchemaName("{Schema}")
            .declareParameters(
                new SqlParameter("ParamIId", Types.INTEGER),
                new SqlParameter("ParamICurrentUserId", Types.INTEGER));
    }

    public PaginatedResult<{Entity}ListItem> findAll(int page, int pageSize,
                                                      String sortBy, String sortOrder,
                                                      String searchFilter) {
        Map<String, Object> params = new HashMap<>();
        params.put("ParamIPage", page);
        params.put("ParamIPageSize", pageSize);
        params.put("ParamISortBy", sortBy);
        params.put("ParamISortOrder", sortOrder);
        params.put("ParamISearchFilter", searchFilter);

        Map<String, Object> result = listProc.execute(params);
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> rows = (List<Map<String, Object>>) result.get("#result-set-1");

        List<{Entity}ListItem> items = rows.stream().map(row -> {
            {Entity}ListItem item = new {Entity}ListItem();
            item.setId((int) row.get("{Entity}Id"));
            item.setName((String) row.get("Name"));
            item.setCode((String) row.get("Code"));
            item.setStatus((String) row.get("Status"));
            item.setCreatedDate((java.sql.Timestamp) row.get("CreatedDate"));
            return item;
        }).toList();

        int totalCount = rows.isEmpty() ? 0 : ((Number) rows.get(0).get("TotalCount")).intValue();

        return new PaginatedResult<>(items, page, pageSize, totalCount);
    }

    public Optional<{Entity}Detail> findById(int id) {
        Map<String, Object> params = new HashMap<>();
        params.put("ParamIId", id);

        Map<String, Object> result = getProc.execute(params);
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> rows = (List<Map<String, Object>>) result.get("#result-set-1");

        if (rows.isEmpty()) return Optional.empty();

        Map<String, Object> row = rows.get(0);
        if (row.containsKey("ErrorCode")) return Optional.empty();

        {Entity}Detail detail = mapRowToDetail(row);
        return Optional.of(detail);
    }

    public {Entity}Detail create(Create{Entity}Request request, int currentUserId) {
        Map<String, Object> params = new HashMap<>();
        params.put("ParamIName", request.getName());
        params.put("ParamICode", request.getCode());
        params.put("ParamIStatus", request.getStatus());
        params.put("ParamICurrentUserId", currentUserId);

        Map<String, Object> result = createProc.execute(params);
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> rows = (List<Map<String, Object>>) result.get("#result-set-1");

        if (rows.isEmpty()) throw new RuntimeException("Failed to create {Entity}");

        return mapRowToDetail(rows.get(0));
    }

    public {Entity}Detail update(int id, Update{Entity}Request request, int currentUserId) {
        Map<String, Object> params = new HashMap<>();
        params.put("ParamIId", id);
        params.put("ParamIName", request.getName());
        params.put("ParamICode", request.getCode());
        params.put("ParamIStatus", request.getStatus());
        params.put("ParamICurrentUserId", currentUserId);

        Map<String, Object> result = updateProc.execute(params);
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> rows = (List<Map<String, Object>>) result.get("#result-set-1");

        if (rows.isEmpty()) throw new RuntimeException("{Entity} not found");

        return mapRowToDetail(rows.get(0));
    }

    public boolean delete(int id, int currentUserId) {
        Map<String, Object> params = new HashMap<>();
        params.put("ParamIId", id);
        params.put("ParamICurrentUserId", currentUserId);

        deleteProc.execute(params);
        return true;
    }

    private {Entity}Detail mapRowToDetail(Map<String, Object> row) {
        {Entity}Detail detail = new {Entity}Detail();
        detail.setId((int) row.get("{Entity}Id"));
        detail.setName((String) row.get("Name"));
        detail.setCode((String) row.get("Code"));
        detail.setStatus((String) row.get("Status"));
        detail.setCreatedBy((int) row.get("CreatedBy"));
        detail.setCreatedDate((java.sql.Timestamp) row.get("CreatedDate"));
        detail.setUpdatedBy((Integer) row.get("UpdatedBy"));
        detail.setUpdatedDate((java.sql.Timestamp) row.get("UpdatedDate"));
        return detail;
    }
}

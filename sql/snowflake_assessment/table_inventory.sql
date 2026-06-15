-- Assessment: List all tables, their row counts, and storage size
SELECT
    table_catalog,
    table_schema,
    table_name,
    table_type,
    row_count,
    bytes / 1024 / 1024 as size_mb,
    last_altered
FROM information_schema.tables
WHERE table_schema NOT IN ('INFORMATION_SCHEMA')
ORDER BY row_count DESC;

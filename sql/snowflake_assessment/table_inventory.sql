-- Snowflake Table Inventory & Assessment
-- Purpose: Generate a high-level inventory of tables for migration assessment.

SELECT
    table_catalog AS database_name,
    table_schema AS schema_name,
    table_name,
    table_type,
    row_count,
    bytes / 1024 / 1024 AS size_mb,
    last_altered AS last_modified,
    CASE
        WHEN row_count > 1000000000 THEN 'LARGE'
        WHEN row_count > 100000000 THEN 'MEDIUM'
        ELSE 'SMALL'
    END AS size_category
FROM information_schema.tables
WHERE table_schema NOT IN ('INFORMATION_SCHEMA', 'PUBLIC')
ORDER BY row_count DESC;

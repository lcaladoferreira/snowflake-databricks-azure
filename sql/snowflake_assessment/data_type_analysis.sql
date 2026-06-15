-- Assessment: Identify Databricks-sensitive or complex data types (e.g., VARIANT, OBJECT, ARRAY)
SELECT
    table_schema,
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE data_type IN ('VARIANT', 'OBJECT', 'ARRAY', 'GEOGRAPHY', 'GEOMETRY')
AND table_schema NOT IN ('INFORMATION_SCHEMA')
ORDER BY table_name;

-- Snowflake Data Type Analysis
-- Purpose: Identify complex or sensitive data types that require special handling in Databricks.

SELECT
    table_schema,
    table_name,
    column_name,
    data_type,
    character_maximum_length,
    numeric_precision,
    is_nullable,
    CASE
        WHEN data_type IN ('VARIANT', 'OBJECT', 'ARRAY') THEN 'COMPLEX_TYPE'
        WHEN data_type IN ('GEOGRAPHY', 'GEOMETRY') THEN 'SPATIAL_TYPE'
        ELSE 'STANDARD'
    END AS handling_category
FROM information_schema.columns
WHERE table_schema NOT IN ('INFORMATION_SCHEMA', 'PUBLIC')
AND (data_type IN ('VARIANT', 'OBJECT', 'ARRAY', 'GEOGRAPHY', 'GEOMETRY') OR character_maximum_length > 2000)
ORDER BY table_name, ordinal_position;

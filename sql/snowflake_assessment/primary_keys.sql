-- Assessment: Find Primary Keys to help with Silver layer deduplication logic
SELECT
    constraint_schema,
    table_name,
    constraint_name,
    column_name,
    ordinal_position
FROM information_schema.key_column_usage
WHERE constraint_name LIKE 'PK%' OR constraint_name LIKE 'PRIMARY%'
ORDER BY table_name, ordinal_position;

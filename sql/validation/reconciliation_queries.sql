-- Reconciliation: Compare row counts between Snowflake and Databricks
-- These would be run after migration is complete.

-- Snowflake side (Assumed)
-- SELECT count(*) FROM RAW_DB.PUBLIC.CUSTOMERS;

-- Databricks side
SELECT 'customers' as table_name, count(*) as row_count FROM migration_prod.bronze.customers
UNION ALL
SELECT 'orders' as table_name, count(*) as row_count FROM migration_prod.bronze.orders;

-- Null checks
SELECT
    count(*) as total_rows,
    count(customer_id) as non_null_ids,
    count(*) - count(customer_id) as null_customer_ids
FROM migration_prod.silver.customers;

-- Metric validation: Compare total revenue
-- Snowflake: SELECT sum(payment_amount) FROM PAYMENTS WHERE status = 'success';
SELECT sum(payment_amount) as total_revenue_gold
FROM migration_prod.gold.fact_orders
WHERE status = 'COMPLETED';

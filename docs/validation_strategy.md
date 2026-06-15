# Validation Strategy

Ensuring data integrity during migration is critical. We use a multi-tiered validation approach.

## 1. Technical Validation
- **Schema Comparison**: Ensure column names, types, and nullability match (within reason) between Snowflake and Databricks.
- **Row Counts**: Simple `COUNT(*)` comparison for every table migrated.

## 2. Statistical Validation
- **Null Counts**: Compare null counts for critical columns (e.g., PKs, FKs, amounts).
- **Distinct Counts**: Verify cardinality of dimensions.
- **Aggregates**: SUM of numeric columns (revenue, quantity) must match between systems.

## 3. Row-Level Validation (Reconciliation)
- **Hashing**: For high-value tables, we calculate a MD5/SHA2 hash of the row content in both Snowflake and Databricks and compare the results.

## Reporting
- A reconciliation report is generated after each migration batch, highlighting any discrepancies for manual review.

# Migration Strategy: Snowflake to Databricks

Migration from Snowflake to Databricks involves more than just moving data; it requires a shift in how data is managed, governed, and processed.

## Phased Approach

### Phase 1: Discovery & Assessment
- **Inventory**: Identify all databases, schemas, tables, and views in Snowflake.
- **Complexity Analysis**: Evaluate Snowflake-specific SQL (e.g., variants, UDFs) that needs translation to Spark SQL or PySpark.
- **Usage Audit**: Identify high-priority vs. dormant tables to optimize migration effort.

### Phase 2: Foundation Setup
- Configure Azure ADLS Gen2 storage accounts.
- Set up Databricks Workspaces and Unity Catalog.
- Establish connectivity between Snowflake and Azure.

### Phase 3: Data Migration (The "Initial Load")
- Bulk export Snowflake tables to ADLS Gen2.
- Use Databricks `COPY INTO` or Auto Loader for high-performance ingestion into Bronze Delta tables.

### Phase 4: Code Migration
- Refactor Snowflake Tasks/Stored Procedures into Databricks Workflows and PySpark/SQL jobs.
- Transform data through Silver and Gold layers.

### Phase 5: Validation & Cutover
- Run reconciliation scripts to verify data parity.
- Parallel run: Operate both systems for a period.
- Final cutover of BI tools and applications to Databricks.

## Technical Considerations

### Data Types
- Snowflake `VARIANT` -> Databricks `STRUCT` or `JSON` string.
- Snowflake `NUMBER` -> Databricks `DECIMAL` or `DOUBLE`.
- Date/Timestamp formats standardization.

### Identity Management
- Migration of Snowflake roles and grants to Unity Catalog principals and privileges.

### Performance Tuning
- Replace Snowflake clustering keys with Delta Lake Liquid Clustering or Z-Ordering in Databricks.

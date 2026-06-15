# Unity Catalog Governance

Unity Catalog (UC) is the cornerstone of governance in the Databricks Lakehouse.

## Namespace Structure
We use a three-level namespace: `catalog.schema.table`

- **Catalog**: `migration_prod` (or similar)
- **Schemas**:
    - `bronze`: Raw data, restricted access to Data Engineers.
    - `silver`: Cleaned data, accessible by Data Engineers and Data Scientists.
    - `gold`: Curated data, accessible by BI Tools and Analysts.

## Managed vs. External Tables
- **Managed Tables**: Default. UC manages both metadata and data.
- **External Tables**: Metadata in UC, data resides in specific ADLS Gen2 locations. Used for the Landing Zone and occasionally Bronze.

## Security Model
- **Principals**: Users and Service Principals (managed via Entra ID / Azure AD).
- **Grants**:
    - `USE CATALOG`
    - `USE SCHEMA`
    - `SELECT`, `MODIFY`, `CREATE`
- **Row/Column Level Security**: Implemented via UC Functions and Tags.

# Unity Catalog Governance Guide

This document outlines the implementation of Unity Catalog (UC) for the Snowflake-to-Databricks migration project, focusing on data governance, security, and organizational structure.

## 1. Introduction to Unity Catalog

Unity Catalog is Databricks' centralized governance solution for all data and AI assets. In this migration, UC provides:
- **Centralized Access Control**: Single point of management for permissions.
- **Data Lineage**: Automated tracking of data flow from Snowflake extraction to Gold marts.
- **Audit Logging**: Comprehensive logs of who accessed what data and when.
- **Unified Discovery**: A searchable interface for data assets across the workspace.

## 2. Catalog and Schema Structure

We follow a three-level namespace architecture: `catalog.schema.table`.

### 2.1. Catalog Names
- `migration_dev`: Development environment for pipeline testing and data exploration.
- `migration_stg`: Staging environment for UAT and pre-production validation.
- `migration_prod`: Production environment for final analytical workloads.

### 2.2. Schema Names (Medallion Layers)
Inside each catalog, we maintain schemas corresponding to the Medallion layers:
- `landing`: Contains definitions for external tables pointing to raw landing files.
- `bronze`: Stores raw ingested Delta tables.
- `silver`: Stores cleansed and conformed business entities.
- `gold`: Stores analytical marts and reporting fact/dimension tables.

## 3. Governance and Security Model

Access is managed through Functional Groups and Privileges, following the principle of least privilege.

### 3.1. Principal Groups
- `data_engineers`: Owners of the migration catalogs; can create, alter, and drop assets.
- `data_scientists`: Read access to `silver` and `gold` layers; `CREATE FUNCTION` privileges for ML.
- `data_analysts`: Read access only to the `gold` curated layer and SQL Warehouses.
- `automation_sp`: Service Principal for CI/CD and job execution.

### 3.2. Example SQL Grants
```sql
-- Grant usage on catalog
GRANT USAGE ON CATALOG migration_prod TO `data_analysts`;

-- Grant select on all tables in gold schema
GRANT SELECT ON SCHEMA migration_prod.gold TO `data_analysts`;
```

## 4. Managed vs. External Tables

### 4.1. Managed Tables
Used for **Bronze, Silver, and Gold** layers. UC manages the metadata and the underlying data files in the catalog's default storage location. This is the preferred approach for performance and ease of management.

### 4.2. External Tables
Used for the **Landing** schema. These tables point to specific paths in ADLS Gen2 where the `SnowflakeExtractor` drops raw Parquet files. This allows UC to govern the files without taking full ownership of the lifecycle.

## 5. Data Lineage and Auditing

- **Automated Lineage**: UC captures lineage at the table and column level for all Spark SQL and PySpark operations. This is used to track how Snowflake source columns propagate to Gold metrics.
- **Audit Logs**: All metadata operations (e.g., `CREATE TABLE`, `GRANT`) and data access events are captured. Logs are exported to a dedicated system schema for security monitoring.
- **PII Discovery**: UC's built-in classifiers help identify sensitive data, which we then tag with `PII` or `Sensitive` metadata tags to trigger dynamic masking policies.

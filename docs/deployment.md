# Deployment Guide

## 1. Azure Infrastructure (Terraform)
The `infra/` directory contains Terraform code to provision the required Azure footprint:
- **Storage**: ADLS Gen2 with specific containers (`landing`, `bronze`, etc.).
- **Compute**: Azure Databricks Workspace (Premium SKU).
- **Security**: Azure Key Vault for secret management.

```bash
cd infra
terraform init
terraform plan
terraform apply
```

## 2. Snowflake Configuration
Ensure the following are available in Snowflake:
- A dedicated `MIGRATION_USER` with `USAGE` on the Database/Schema and `SELECT` on all tables.
- A Warehouse (e.g., `MIGRATION_WH`) for extraction compute.

## 3. Databricks Asset Bundles (DABs)
We use DABs for CI/CD. Configuration is in `databricks.yml`.

### Authentication
```bash
databricks auth login --host https://adb-<workspace-id>.azuredatabricks.net
```

### Deploying to Dev
```bash
databricks bundle deploy -t dev
```

## 4. Unity Catalog Setup
Run the scripts in `sql/unity_catalog/setup.sql` in a Databricks SQL Warehouse to:
1.  Create Catalogs and Schemas.
2.  Define External Locations.
3.  Set up Grants for Engineers and Analysts.

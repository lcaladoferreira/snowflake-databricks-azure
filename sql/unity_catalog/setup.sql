-- unity_catalog_setup.sql
-- Production governance for Medallion Architecture

-- 1. External Locations & Storage Credentials
-- Assumes Terraform has created the storage account and managed identity
CREATE STORAGE CREDENTIAL IF NOT EXISTS `azure_storage_cred`
  IDENTIFIER `managed-identity-id`
  COMMENT 'Managed Identity for ADLS access';

CREATE EXTERNAL LOCATION IF NOT EXISTS `landing_zone`
  URL 'abfss://landing@stmigrationprod001.dfs.core.windows.net/'
  STORAGE CREDENTIAL `azure_storage_cred`;

-- 2. Catalog & Schemas
CREATE CATALOG IF NOT EXISTS migration_prod;
USE CATALOG migration_prod;

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- 3. Security Roles & Grants
CREATE GROUP IF NOT EXISTS `data_engineers`;
CREATE GROUP IF NOT EXISTS `data_analysts`;

-- Data Engineer Permissions (Full access to all layers)
GRANT USAGE ON CATALOG migration_prod TO `data_engineers`;
GRANT ALL PRIVILEGES ON SCHEMA bronze TO `data_engineers`;
GRANT ALL PRIVILEGES ON SCHEMA silver TO `data_engineers`;
GRANT ALL PRIVILEGES ON SCHEMA gold TO `data_engineers`;

-- Data Analyst Permissions (Read-only Gold)
GRANT USAGE ON CATALOG migration_prod TO `data_analysts`;
GRANT USE SCHEMA ON SCHEMA gold TO `data_analysts`;
GRANT SELECT ON ALL TABLES IN SCHEMA gold TO `data_analysts`;

-- 4. PII Tagging Example
ALTER TABLE silver.customers ALTER COLUMN email SET TAGS ('pii' = 'true');

-- 5. Row-Level Security Example (Template)
-- CREATE FUNCTION gold.customer_mask(email STRING)
-- RETURN IF(IS_ACCOUNT_GROUP_MEMBER('data_engineers'), email, 'MASKED');
-- ALTER TABLE gold.dim_customers ALTER COLUMN email SET MASK gold.customer_mask;

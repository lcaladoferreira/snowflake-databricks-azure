-- 1. Create Catalog
CREATE CATALOG IF NOT EXISTS migration_prod;
USE CATALOG migration_prod;

-- 2. Create Schemas
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- 3. Managed Table Examples
-- (Tables are typically created via Spark jobs, but can be defined here)
CREATE TABLE IF NOT EXISTS gold.dim_customers (
    customer_id INT,
    first_name STRING,
    last_name STRING,
    email STRING,
    registration_date TIMESTAMP
) TBLPROPERTIES (delta.enableChangeDataFeed = true);

-- 4. External Location Example
-- CREATE EXTERNAL LOCATION landing_zone
-- URL 'abfss://landing@stdatalakeprod.dfs.core.windows.net/'
-- WITH (STORAGE CREDENTIAL `azure-storage-credential`);

-- 5. Grants and Permissions
GRANT USAGE ON CATALOG migration_prod TO `data-analysts`;
GRANT USE SCHEMA ON SCHEMA gold TO `data-analysts`;
GRANT SELECT ON ALL TABLES IN SCHEMA gold TO `data-analysts`;

GRANT USAGE ON CATALOG migration_prod TO `data-engineers`;
GRANT ALL PRIVILEGES ON SCHEMA bronze TO `data-engineers`;
GRANT ALL PRIVILEGES ON SCHEMA silver TO `data-engineers`;
GRANT ALL PRIVILEGES ON SCHEMA gold TO `data-engineers`;

# Security Architecture

## 1. Authentication
- **Azure**: Service Principals are used for all automated CI/CD and Job executions.
- **Snowflake**: Key-Pair authentication is the recommended production standard (though password is provided as a template).

## 2. Authorization (Unity Catalog)
- **Least Privilege**: Users are granted access only to the Gold layer. Bronze and Silver are restricted to Data Engineers.
- **Managed Identities**: Databricks uses Managed Identities to access ADLS Gen2, removing the need for storage account keys in code.

## 3. Data Protection
- **Encryption**: All data is encrypted at rest via Azure Storage Service Encryption (SSE) and in transit via TLS 1.2+.
- **PII Governance**: Unity Catalog tags are used to identify PII columns. Row-level security and dynamic masking can be applied based on these tags.
- **Secrets**: All credentials (Snowflake password, Databricks tokens) must be stored in **Azure Key Vault** and accessed via Databricks Secret Scopes.

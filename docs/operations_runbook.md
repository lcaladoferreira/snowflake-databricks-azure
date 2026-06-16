# Operations Runbook

This runbook provides guidance for maintaining, monitoring, and troubleshooting the Snowflake-to-Databricks migration pipeline.

## 1. Monitoring and Observability

### 1.1. Databricks Job Alerts
All jobs are configured with email/Slack notifications:
- **On Failure**: High-priority alert sent to the Data Engineering on-call team.
- **On SLA Warning**: Sent if the job takes 50% longer than the historical average.

### 1.2. Logging and Metadata
Pipeline logs are captured in two locations:
- **Standard Out/Error**: Accessible via the Databricks Job Run UI.
- **Metadata Tables**: Detailed execution logs, including batch IDs and row counts, are stored in `migration_prod.metadata.execution_logs`.

## 2. Common Troubleshooting Steps

### 2.1. Extraction Failures (Snowflake-to-Landing)
- **Symptom**: `SnowflakeExtractor` fails with connection errors.
- **Resolution**:
  1. Check Snowflake service status.
  2. Verify that the Snowflake credentials in Azure Key Vault haven't expired.
  3. Ensure the Databricks Cluster has network connectivity to the Snowflake endpoint.

### 2.2. Schema Mismatch in Bronze
- **Symptom**: Auto Loader fails to process a file due to schema drift.
- **Resolution**:
  1. Inspect the file in the landing zone to identify the new/changed column.
  2. If the change is expected, update the `schema_evolution_mode` or manually evolve the Bronze table schema.
  3. Re-run the ingestion task.

### 2.3. Data Quality Failures in Silver
- **Symptom**: `SilverTransformer` identifies unexpected nulls or duplicate keys.
- **Resolution**:
  1. Query the Bronze table for the problematic records using the `batch_id` from the logs.
  2. Adjust cleaning logic in `jobs/silver/` if the source data format has changed.
  3. Use the `RESTORE` command to revert the Silver table to a previous state if corruption occurred.

## 3. Maintenance Tasks

### 3.1. Performance Tuning
- **Optimize**: Run `OPTIMIZE` on frequently joined Silver and Gold tables to improve query performance.
- **Vacuum**: Periodic `VACUUM` (default 7 days) to remove stale data files and reduce storage costs.

### 3.2. Watermark Resets
If a historical reload is required:
1. Identify the table and the desired start date.
2. Update the `last_watermark` value in the `metadata/extraction_metadata.json` file.
3. Re-run the `SnowflakeExtractor` for that specific table.

## 4. Disaster Recovery

In the event of a region-level failure:
1. **Azure Site Recovery**: Follow the standard organizational procedure for failing over ADLS Gen2 and Key Vault.
2. **Workspace Reconstruction**: Use Terraform to redeploy the Databricks workspace and Unity Catalog configurations to the secondary region.
3. **Pipeline Re-trigger**: Start the pipeline from the last successful extraction batch.

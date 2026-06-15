# Operations Runbook

## Monitoring
- **Databricks SQL Warehouse**: Monitor for query performance and cost.
- **Job Clusters**: Track job success/failure in the Databricks UI or via API.
- **Unity Catalog Audit Logs**: Monitor who is accessing what data.

## Incident Management
1. **Job Failure**:
    - Check Databricks Job logs.
    - Check `_last_ingestion_timestamp` in Bronze to identify where it stopped.
2. **Data Discrepancy**:
    - Run the `src/validation/reconciler.py` script for the affected table.
    - Investigate if the issue is in the Extraction or Transformation logic.

## Deployment
- CI/CD via GitHub Actions.
- Use `databricks-cli` or `terraform` for workspace and job deployments.
- Never hardcode secrets; use Databricks Secrets Scopes.

# Production Hardening Checklist

### Infrastructure
- [ ] Azure Key Vault secrets rotated.
- [ ] ADLS Gen2 diagnostic logs enabled.
- [ ] Managed Identity assigned to Databricks Access Connector.

### Data Engineering
- [ ] Snowflake watermarks validated.
- [ ] Silver layer deduplication keys verified with business owners.
- [ ] Gold fact/dimension relationships (FKs) validated.
- [ ] Auto Loader `cloudFiles` configuration tuned for production volume.

### Quality & Governance
- [ ] Reconciliation thresholds (max allowable variance) defined.
- [ ] Unity Catalog PII tags applied.
- [ ] Data Analysts given `SELECT` access to Gold schema.

### Operations
- [ ] Databricks Workflow failure alerts (Email/PagerDuty) configured.
- [ ] CI/CD branch protection rules enabled on `main` and `develop`.
- [ ] Runbook shared with On-Call team.

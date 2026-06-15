# Migration Strategy Guide

This document outlines the phased approach for migrating enterprise data workloads from Snowflake to Azure Databricks.

## 1. Phased Migration Approach

A successful migration is conducted in four distinct phases to minimize business disruption and ensure data parity.

### Phase 1: Discovery & Assessment
- **Inventory**: Identifying all schemas, tables, views, and stored procedures in Snowflake.
- **Complexity Analysis**: Categorizing tables by size and complexity (e.g., standard vs. complex types like `VARIANT`).
- **Dependency Mapping**: Mapping downstream BI tools and analytical applications.
- **Tooling**: Running the scripts in `sql/snowflake_assessment/` to generate an automated inventory report.

### Phase 2: Pilot & Foundation
- **Infrastructure**: Provisioning the Azure footprint (ADLS Gen2, Databricks, Unity Catalog) via Terraform.
- **Pilot Ingestion**: Migrating a subset of high-value tables (e.g., Customers, Orders) using the `SnowflakeExtractor` in `demo` then `production` mode.
- **Validation**: Testing the end-to-end Medallion flow (Bronze -> Silver -> Gold) for the pilot entities.

### Phase 3: Bulk Migration
- **Parallel Load**: Executing chunked extractions for large Fact tables.
- **Orchestration**: Deploying Databricks Workflows via Asset Bundles to handle high-concurrency ingestion.
- **Refactoring**: Porting Snowflake SQL tasks and stored procedures to PySpark and Spark SQL in Databricks.

### Phase 4: Validation & Cutover
- **Reconciliation**: Running the `ReconciliationEngine` to prove parity (details below).
- **Parallel Run**: Operating both systems in sync for a defined period (e.g., 2 weeks).
- **Cutover**: Redirecting Power BI, Tableau, or other consumers to the Databricks SQL Warehouse.

## 2. Reconciliation Strategy

Maintaining trust in the data during migration is paramount. We implement a multi-tiered reconciliation strategy.

### 2.1. Technical Parity
Using the `ReconciliationEngine` in `src/validation/`, we perform:
- **Row Count Validation**: Ensuring the count in Snowflake matches the count in the Databricks Bronze layer.
- **Null Count Check**: Identifying if any data loss occurred during the Parquet-to-Delta casting process.
- **Range Checks**: Comparing MIN and MAX values for primary keys and watermark columns.

### 2.2. Business Parity (Metrics)
For the Gold layer, we validate calculated metrics:
- **Aggregate Checksums**: Comparing the `SUM(payment_amount)` between Snowflake and `fact_orders`.
- **Dimensional Cardinality**: Ensuring the number of unique products and customers matches the source.

### 2.3. Failure Thresholds
The `ReconciliationEngine` logs results to `gold.reconciliation_results`.
- **Critical Failure**: Any mismatch in Row Counts or Numeric Checksums triggers a pipeline stop and alert.
- **Warning**: Mismatches in technical metadata or non-critical nulls are logged for manual review but do not halt the process.

## 3. Rollback Plan

In the event of a critical failure during Phase 4 (Cutover), the following steps are defined:
1. **Redirect Traffic**: Immediately switch BI tool connections back to the Snowflake host.
2. **Analysis**: Inspect the `reconciliation_results` table and Databricks Job logs to identify the point of failure.
3. **Purge & Reload**: If data corruption is identified, the affected Delta layers are purged, and the pipeline is re-triggered with fixed logic.

## 4. SLA & Data Freshness Targets

The target SLA for the migrated platform is:
- **Data Freshness**: T+1 for bulk loads, 1 hour for incremental orders.
- **System Availability**: 99.9% uptime for the Databricks SQL Warehouse.
- **Validation Completion**: Reconciliation reports must be generated and pass within 30 minutes of Gold layer completion.

## 5. Production Hardening

Before final sign-off, the checklist in `docs/production_hardening_checklist.md` must be completed, covering security audits, performance tuning, and operational alerting setup.

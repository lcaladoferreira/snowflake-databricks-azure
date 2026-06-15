# Snowflake to Azure Databricks Migration Accelerator

A production-grade, enterprise-ready framework for migrating data workloads from Snowflake to the Azure Databricks Lakehouse.

## 🚀 Key Features

- **Enterprise Extraction**: High-performance, chunked Snowflake extraction with incremental watermark support.
- **Medallion Architecture**: Fully implemented Bronze, Silver, and Gold layers using Delta Lake 3.x and Unity Catalog.
- **Infrastructure as Code**: Terraform modules for Azure and Databricks resource provisioning.
- **Modern Orchestration**: Databricks Asset Bundles (DABs) for CI/CD and workflow management.
- **Unity Catalog Governance**: Least-privilege security model, PII tagging, and external location management.
- **Automated Reconciliation**: Deep parity validation between Snowflake and Databricks with persistent results.
- **Professional CI/CD**: Comprehensive GitHub Actions for linting, testing, and deployment validation.

## 🏗️ Architecture

The accelerator follows the **Medallion Architecture** governed by **Unity Catalog**.

1.  **Snowflake (Source)**: Tables and Views.
2.  **Landing (ADLS Gen2)**: Raw Parquet files, partitioned and chunked.
3.  **Bronze (Unity Catalog)**: 1:1 raw ingestion with technical metadata (Auto Loader).
4.  **Silver (Unity Catalog)**: Cleaned, deduped, and conformed entities (Delta Merge).
5.  **Gold (Unity Catalog)**: Analytical Star Schema (Dims/Facts) and specialized Data Marts.

## 📂 Repository Structure

- `infra/`: Terraform modules for Azure infrastructure.
- `src/`: Core Python logic (Extraction, Config, Validation).
- `jobs/`: Medallion layer PySpark transformation jobs.
- `bundles/`: Databricks Asset Bundle resource definitions.
- `sql/`: SQL scripts for Unity Catalog and Snowflake assessment.
- `tests/`: Comprehensive unit testing suite.
- `docs/`: Detailed technical documentation.

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+
- Databricks CLI
- Terraform 1.5+
- Snowflake Account with SELECT permissions.

### Deployment
1.  **Infrastructure**:
    ```bash
    cd infra
    terraform init
    terraform apply
    ```
2.  **Databricks Bundle**:
    ```bash
    databricks bundle deploy -t dev
    ```

### Running the Pipeline
- **Demo Mode**: `export EXECUTION_MODE=demo && python src/main.py`
- **Production**: Trigger the `migration_pipeline` job in Databricks Workflows.

## 📄 Documentation
- [Architecture & Design](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [Migration Strategy](docs/migration_strategy.md)
- [Unity Catalog Governance](docs/unity_catalog.md)
- [Reconciliation & Quality](docs/reconciliation.md)

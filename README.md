# Snowflake to Databricks Migration Accelerator

This project is a production-oriented data engineering accelerator demonstrating a complete migration architecture from Snowflake to Databricks on Azure. It implements a Medallion Architecture (Bronze, Silver, Gold) governed by Unity Catalog, with automated validation and reconciliation.

## Project Overview

The goal is to provide a robust, reusable framework for migrating data workloads from Snowflake to Databricks. The architecture follows industry best practices for modern data lakehouses on Azure.

### Target Architecture

1.  **Source**: Snowflake (Databases/Schemas/Tables)
2.  **Landing Zone**: Azure Data Lake Storage Gen2 (Raw CSV/Parquet)
3.  **Bronze Layer**: Delta Lake (Opaque ingestion, metadata added)
4.  **Silver Layer**: Delta Lake (Cleaned, filtered, conformed, standardized)
5.  **Gold Layer**: Delta Lake (Star schema, business-level aggregates, metrics)
6.  **Governance**: Unity Catalog (Catalogs, Schemas, Tables, Grants)
7.  **Validation**: Automated reconciliation between Snowflake and Databricks

## Key Features

- **Dual Execution Modes**:
    - `Demo`: Runs locally using synthetic data (no cloud credentials required).
    - `Production`: Template for real Snowflake-to-Azure Databricks migration.
- **Automated Assessment**: SQL scripts for Snowflake environment analysis.
- **Medallion Architecture**: Fully implemented PySpark jobs for Bronze, Silver, and Gold.
- **Data Validation**: Comprehensive reconciliation scripts (row counts, null checks, checksums).
- **Unity Catalog Integration**: SQL templates for modern data governance.
- **Production Ready**: Structured for CI/CD, testing, and operational monitoring.

## Repository Structure

```text
├── .github/workflows/      # CI/CD pipelines
├── data/                   # Sample and local data storage
│   ├── sample/             # Synthetic CSVs for demo mode
│   └── raw/                # Simulated landing zone
├── docs/                   # Detailed technical documentation
├── jobs/                   # PySpark transformation jobs
│   ├── bronze/             # Raw to Bronze ingestion
│   ├── silver/             # Bronze to Silver transformation
│   └── gold/               # Silver to Gold (Star Schema)
├── sql/                    # SQL scripts
│   ├── snowflake_assessment/ # Source analysis scripts
│   ├── unity_catalog/      # Governance setup
│   └── validation/         # Reconciliation queries
├── src/                    # Core Python package
│   ├── config/             # Configuration management
│   ├── extraction/         # Extraction logic (Snowflake/Local)
│   ├── utils/              # Spark and logging helpers
│   └── validation/         # Reconciliation engine logic
├── tests/                  # Unit and integration tests
├── .env.example            # Environment variable template
├── pyproject.toml          # Project metadata and dependencies
└── requirements.txt        # Python dependencies
```

## Getting Started (Demo Mode)

To run the migration pipeline locally without a Snowflake or Azure account:

1.  **Clone the repository**:
    ```bash
    git clone <repo-url>
    cd snowflake-to-databricks-migration
    ```

2.  **Set up environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Generate sample data**:
    ```bash
    python scripts/generate_sample_data.py
    ```

4.  **Run the demo pipeline**:
    ```bash
    export EXECUTION_MODE=demo
    python src/main.py
    ```

## Production Migration Steps

1.  **Assessment**: Run scripts in `sql/snowflake_assessment/` on Snowflake.
2.  **Configuration**: Update `.env` with Azure and Snowflake credentials.
3.  **Deployment**: Use CI/CD to deploy jobs to Databricks.
4.  **Extraction**: Execute `src/extraction/extractor.py` to move data to ADLS Gen2.
5.  **Processing**: Schedule Medallion jobs in Databricks Workflows.
6.  **Validation**: Run `src/validation/reconciler.py` to ensure data integrity.

## Documentation

See the [docs/](docs/) directory for detailed information on:
- [Architecture](docs/architecture.md)
- [Migration Strategy](docs/migration_strategy.md)
- [Data Modeling](docs/data_model.md)
- [Unity Catalog Setup](docs/unity_catalog.md)
- [Validation Strategy](docs/validation_strategy.md)
- [Operations Runbook](docs/operations_runbook.md)

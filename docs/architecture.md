# Architecture Overview

This project implements a production-grade migration architecture from Snowflake to Azure Databricks.

## High-Level Flow

1.  **Snowflake (Source)**: Data is extracted using a custom `SnowflakeExtractor` supporting chunking and watermarks.
2.  **Landing (ADLS Gen2)**: Data is landed as snappy-compressed Parquet files, partitioned by `batch_id`.
3.  **Bronze (Delta Lake)**: Data is ingested using Auto Loader (Production) or Batch (Demo), adding technical metadata.
4.  **Silver (Delta Lake)**: Standardized and deduplicated tables. Idempotent MERGE logic handles updates and prevents duplicates.
5.  **Gold (Delta Lake)**: Star Schema (Dimensions/Facts) and Analytical Data Marts (Daily Sales, CLV, etc.) optimized with Z-Ordering.
6.  **Governance (Unity Catalog)**: All Delta tables are managed within Unity Catalog with a three-level namespace.

## Component Details

### Extraction Layer (`src/extraction/`)
- Supports full and incremental loads.
- Implements chunked extraction for memory efficiency.
- Metadata audit log tracks every batch and watermark.

### Medallion Processing (`jobs/`)
- **Bronze**: Focuses on raw data preservation and technical metadata enrichment.
- **Silver**: Implements business logic, data cleaning, and deduplication.
- **Gold**: Optimized for query performance and business reporting.

### Infrastructure & Orchestration
- **Terraform**: Provisions RG, ADLS, Key Vault, and Databricks.
- **Databricks Asset Bundles**: Manages deployments and job workflows.
- **GitHub Actions**: Automates testing, linting, and infrastructure validation.

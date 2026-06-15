# Cost Optimization & Performance

## 1. Databricks Compute
- **Serverless SQL**: Used for ad-hoc analysis to minimize idle compute costs.
- **Job Clusters**: Used for all migration tasks. They are significantly cheaper than All-Purpose clusters.
- **Photon**: Enabled for complex Silver and Gold transformations to reduce execution time.

## 2. Delta Lake Performance
- **Liquid Clustering**: Implemented on large Fact tables to replace traditional partitioning.
- **Optimize & Vacuum**: Automated maintenance tasks to reorganize files and remove expired data.
- **Z-Order**: Applied to frequently filtered columns (e.g., `customer_id`, `order_date`).

## 3. Storage
- **Lifecycle Management**: Landing zone files are moved to Archive tier or deleted after successful ingestion into Bronze.
- **Delta Deletion**: Vacuum settings are tuned to balance data recovery needs vs. storage costs.

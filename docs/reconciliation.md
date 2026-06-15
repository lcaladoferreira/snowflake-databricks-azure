# Reconciliation & Data Quality

## Reconciliation Engine
The engine in `src/validation/reconciliation_engine.py` is a critical production component. It ensures parity between Snowflake and Databricks.

### Metrics Validated:
1.  **Row Count**: Total record parity.
2.  **Null Count**: Ensuring no data was lost or corrupted during casting.
3.  **Range Checks**: Min/Max values for dates and IDs.
4.  **Checksums**: SUM of numeric columns (e.g., `payment_amount`) between source and target.

### Persistance:
All results are stored in `gold.reconciliation_results` Delta table for audit and historical tracking.

## Data Quality (Silver Layer)
- **Schema Enforcement**: Bronze layer uses strict schema validation.
- **Deduplication**: Silver layer uses `Window` functions to ensure only the latest record is kept per Business Key.
- **Merge Logic**: Uses Delta Lake `MERGE` for idempotent upserts.

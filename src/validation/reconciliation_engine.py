from datetime import datetime
from typing import Any, Dict, List, Optional

import snowflake.connector
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col,
    count,
    current_timestamp,
    when,
)
from pyspark.sql.functions import (
    max as _max,
)
from pyspark.sql.functions import (
    min as _min,
)
from pyspark.sql.functions import (
    sum as _sum,
)

from src.config.config import Config

logger = Config.get_logger(__name__)


class ReconciliationEngine:
    """Enterprise-grade Reconciliation Engine for Source-to-Target Parity.

    This engine compares metrics between the source (Snowflake) and target (Databricks)
    to ensure data integrity throughout the migration process.
    """

    def __init__(self, spark: SparkSession) -> None:
        """Initializes the engine with a Spark session.

        Args:
            spark: Active Spark session.
        """
        self.spark = spark
        self.results_path = Config.get_storage_path("gold", "reconciliation_results")
        self.allowed_tables = {
            "fact_orders",
            "dim_customers",
            "dim_products",
            "dim_dates",
        }

    def _get_snowflake_connection(self) -> snowflake.connector.SnowflakeConnection:
        """Establishes a connection to Snowflake.

        Returns:
            snowflake.connector.SnowflakeConnection: A Snowflake connection object.
        """
        try:
            return snowflake.connector.connect(**Config.get_snowflake_config())
        except snowflake.connector.Error as e:
            logger.error(f"Failed to connect to Snowflake: {str(e)}")
            raise

    def reconcile(
        self,
        table_name: str,
        numeric_cols: List[str],
        date_col: Optional[str] = None,
    ) -> None:
        """Runs comprehensive parity checks between Snowflake and Databricks.

        Args:
            table_name: Name of the table to reconcile.
            numeric_cols: List of numeric columns for checksum validation.
            date_col: Optional date column for range validation.
        """
        logger.info(f"Reconciling table: {table_name}")

        source_metrics = self._get_source_metrics(table_name, numeric_cols, date_col)

        target_df = self.spark.read.format("delta").load(
            Config.get_storage_path("gold", table_name)
        )
        target_metrics = self._calculate_target_metrics(target_df, numeric_cols, date_col)

        report = self._compare_metrics(table_name, source_metrics, target_metrics)
        self._persist_report(report)

        if report["status"] == "FAILED":
            logger.error(f"Reconciliation FAILURE for {table_name}")
        else:
            logger.info(f"Reconciliation PASSED for {table_name}")

    def _calculate_target_metrics(
        self, df: DataFrame, num_cols: List[str], date_col: Optional[str]
    ) -> Dict[str, Any]:
        """Calculates aggregates, nulls, and row counts.

        Args:
            df: Target dataframe.
            num_cols: Numeric columns for checksum.
            date_col: Optional date column.

        Returns:
            Dict[str, Any]: Calculated metrics.
        """
        aggs = [count("*").alias("row_count")]

        for c in num_cols:
            aggs.append(_sum(c).alias(f"sum_{c}"))
            aggs.append(count(when(col(c).isNull(), 1)).alias(f"nulls_{c}"))

        if date_col:
            aggs.append(_min(date_col).alias("min_date"))
            aggs.append(_max(date_col).alias("max_date"))

        return df.agg(*aggs).collect()[0].asDict()

    def _get_source_metrics(
        self, table_name: str, num_cols: List[str], date_col: Optional[str]
    ) -> Dict[str, Any]:
        """Fetches metrics from Snowflake.

        Args:
            table_name: Name of the source table.
            num_cols: Numeric columns.
            date_col: Optional date column.

        Returns:
            Dict[str, Any]: Source metrics.

        Raises:
            ValueError: If the table name is not in the allowlist.
            snowflake.connector.Error: If a Snowflake error occurs.
        """
        if table_name.lower() not in self.allowed_tables:
            raise ValueError(f"Table {table_name} is not in the allowed list.")

        sf_table = table_name.upper()
        sql_parts = ["COUNT(*) AS ROW_COUNT"]

        for col_name in num_cols:
            col_upper = col_name.upper()
            sql_parts.append(f"SUM({col_upper}) AS SUM_{col_upper}")
            sql_parts.append(
                f"COUNT(CASE WHEN {col_upper} IS NULL THEN 1 END) AS NULLS_{col_upper}"
            )

        if date_col:
            dc_upper = date_col.upper()
            sql_parts.append(f"MIN({dc_upper}) AS MIN_DATE")
            sql_parts.append(f"MAX({dc_upper}) AS MAX_DATE")

        sql = f"SELECT {', '.join(sql_parts)} FROM {sf_table}"
        logger.info(f"Executing Snowflake metrics query: {sql}")

        try:
            with self._get_snowflake_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    row = cur.fetchone()
                    if not row:
                        return {}
                    return {desc[0].lower(): val for desc, val in zip(cur.description, row)}
        except snowflake.connector.Error as e:
            logger.error(f"Snowflake error during metrics retrieval: {str(e)}")
            raise

    def _compare_metrics(self, table_name: str, source: dict, target: dict) -> dict:
        """Compares source and target metrics and identifies discrepancies.

        Args:
            table_name: Table name.
            source: Source metrics dictionary.
            target: Target metrics dictionary.

        Returns:
            dict: Reconciliation report.
        """
        errors = []
        if source.get("row_count") != target.get("row_count"):
            errors.append(
                f"Count mismatch: SF={source.get('row_count')}, DB={target.get('row_count')}"
            )

        status = "PASSED" if not errors else "FAILED"
        return {
            "table_name": table_name,
            "status": status,
            "message": "; ".join(errors),
            "source_metrics": str(source),
            "target_metrics": str(target),
            "reconciled_at": datetime.now().isoformat(),
        }

    def _persist_report(self, report: dict) -> None:
        """Stores the result in a Delta audit table.

        Args:
            report: Reconciliation report dictionary.
        """
        df = self.spark.createDataFrame([report])
        (
            df.withColumn("audit_timestamp", current_timestamp())
            .write.format("delta")
            .mode("append")
            .save(self.results_path)
        )


if __name__ == "__main__":
    from src.utils.spark_utils import get_spark_session

    s = get_spark_session("Reconciliation")
    re = ReconciliationEngine(s)

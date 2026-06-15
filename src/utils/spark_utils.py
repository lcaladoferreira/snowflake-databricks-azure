"""Spark utilities for the migration accelerator.

Handles the initialization and configuration of Spark sessions for both
local (demo) and Databricks (production) environments.
"""

from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip
from src.config.config import Config

def get_spark_session(app_name: str = "SnowflakeMigration") -> SparkSession:
    """Initializes or retrieves a Spark session.

    Args:
        app_name (str, optional): Name of the Spark application. Defaults to "SnowflakeMigration".

    Returns:
        SparkSession: The initialized Spark session.
    """
    if Config.EXECUTION_MODE == "demo":
        builder = (SparkSession.builder
                .appName(app_name)
                .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
                .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
                .master("local[*]"))
        return configure_spark_with_delta_pip(builder).getOrCreate()
    else:
        # In Databricks, the Spark session is already available
        return SparkSession.builder.getOrCreate()
